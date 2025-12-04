#!/usr/bin/env bash
# Helper script for common staging operations

NAMESPACE="ipno-staging"
PROJECT="excellent-zoo-300106"

case "$1" in
    status|st)
        echo "=== Staging Status ==="
        kubectl get deployments -n $NAMESPACE
        echo ""
        kubectl get pods -n $NAMESPACE
        ;;

    logs)
        SERVICE="${2:-ipno-backend}"
        echo "Streaming logs from $SERVICE..."
        kubectl logs -f deployment/$SERVICE -n $NAMESPACE
        ;;

    exec|shell)
        POD=$(kubectl get pods -n $NAMESPACE -l app=ipno-backend -o jsonpath='{.items[0].metadata.name}')
        echo "Connecting to pod: $POD"
        kubectl exec -it $POD -n $NAMESPACE -- /bin/bash
        ;;

    django|manage)
        shift
        IMAGE_TAG="${1:-backend-staging-latest}"
        shift
        COMMAND="$@"
        if [ -z "$COMMAND" ]; then
            echo "Usage: $0 django [image_tag] <django_command>"
            echo "Example: $0 django backend-staging-latest shell"
            exit 1
        fi
        bin/run_spot_job.sh --staging $IMAGE_TAG $COMMAND
        ;;

    restart)
        SERVICE="${2:-all}"
        if [ "$SERVICE" = "all" ]; then
            echo "Restarting all services..."
            kubectl rollout restart deployment/ipno-backend -n $NAMESPACE
            kubectl rollout restart deployment/celery -n $NAMESPACE
        else
            echo "Restarting $SERVICE..."
            kubectl rollout restart deployment/$SERVICE -n $NAMESPACE
        fi
        ;;

    rollback)
        SERVICE="${2:-ipno-backend}"
        echo "Rolling back $SERVICE..."
        kubectl rollout undo deployment/$SERVICE -n $NAMESPACE
        ;;

    images|img)
        echo "Recent staging images:"
        gcloud container images list-tags us.gcr.io/$PROJECT/ipno-backend \
            --filter="tags:backend-staging*" \
            --limit=10 \
            --format="table(tags,timestamp)"
        ;;

    secrets)
        echo "Available secrets in staging:"
        kubectl get secrets -n $NAMESPACE
        echo ""
        echo "To view a secret value:"
        echo "  kubectl get secret <name> -n $NAMESPACE -o jsonpath='{.data.<key>}' | base64 -d"
        ;;

    configmap|config)
        echo "ConfigMaps in staging:"
        kubectl get configmap ipno -n $NAMESPACE -o yaml
        ;;

    cronjobs|cron)
        echo "Cronjobs in staging:"
        kubectl get cronjobs -n $NAMESPACE
        ;;

    connect|auth)
        echo "Configuring kubectl for GKE..."
        gcloud container clusters get-credentials ipno \
            --zone us-central1-a \
            --project $PROJECT
        kubectl config set-context --current --namespace=$NAMESPACE
        echo "Connected to staging namespace"
        ;;

    *)
        echo "LLEAD Staging Helper"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  status, st              - Show deployment and pod status"
        echo "  logs [service]          - Stream logs (default: ipno-backend)"
        echo "  exec, shell             - Open shell in backend pod"
        echo "  django <cmd>            - Run Django management command"
        echo "  restart [service|all]   - Restart deployments (default: all)"
        echo "  rollback [service]      - Rollback deployment (default: ipno-backend)"
        echo "  images, img             - List recent staging images"
        echo "  secrets                 - List secrets in staging"
        echo "  configmap, config       - Show config maps"
        echo "  cronjobs, cron          - List cronjobs"
        echo "  connect, auth           - Configure kubectl connection"
        echo ""
        echo "Examples:"
        echo "  $0 status"
        echo "  $0 logs celery"
        echo "  $0 django shell"
        echo "  $0 restart ipno-backend"
        echo "  $0 images"
        exit 1
        ;;
esac
