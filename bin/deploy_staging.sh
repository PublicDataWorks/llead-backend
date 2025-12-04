#!/usr/bin/env bash
set -e

echo "================================================"
echo "  LLEAD Backend - Manual Staging Deployment"
echo "================================================"
echo ""

# GKE Configuration
export GOOGLE_PROJECT_ID="excellent-zoo-300106"
export GOOGLE_CLUSTER_NAME="ipno"
export GOOGLE_COMPUTE_ZONE="us-central1-a"

# Staging-specific configuration
export NAMESPACE_ENV="ipno-staging"
export CLOUD_SQL_DATABASE="ipno-database-staging"
export CELERY_NUM_WORKER=2

# Check if image tag is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backend_image_tag> [skip-migrations]"
    echo ""
    echo "Examples:"
    echo "  $0 backend-staging-latest           # Deploy latest staging image"
    echo "  $0 backend-staging-123              # Deploy specific build"
    echo "  $0 backend-staging-latest skip      # Deploy without migrations"
    echo ""
    echo "Available images:"
    gcloud container images list-tags us.gcr.io/$GOOGLE_PROJECT_ID/ipno-backend \
        --filter="tags:backend-staging*" \
        --limit=10 \
        --format="table(tags,timestamp)" 2>/dev/null || echo "  (Run 'gcloud auth login' if you see authentication errors)"
    exit 1
fi

export BACKEND_IMAGE_TAG="$1"
SKIP_MIGRATIONS="$2"

echo "Configuration:"
echo "  Project:        $GOOGLE_PROJECT_ID"
echo "  Cluster:        $GOOGLE_CLUSTER_NAME"
echo "  Namespace:      $NAMESPACE_ENV"
echo "  Database:       $CLOUD_SQL_DATABASE"
echo "  Image Tag:      $BACKEND_IMAGE_TAG"
echo "  Celery Workers: $CELERY_NUM_WORKER"
echo ""

# Verify authentication
echo "Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Error: Not authenticated with Google Cloud. Run 'gcloud auth login'"
    exit 1
fi

# Configure kubectl
echo "Configuring kubectl..."
gcloud container clusters get-credentials $GOOGLE_CLUSTER_NAME \
    --zone $GOOGLE_COMPUTE_ZONE \
    --project $GOOGLE_PROJECT_ID \
    --quiet

# Set namespace context
kubectl config set-context --current --namespace=$NAMESPACE_ENV

# Verify image exists
echo ""
echo "Verifying image exists..."
if ! gcloud container images describe us.gcr.io/$GOOGLE_PROJECT_ID/ipno-backend:$BACKEND_IMAGE_TAG &>/dev/null; then
    echo "Warning: Image us.gcr.io/$GOOGLE_PROJECT_ID/ipno-backend:$BACKEND_IMAGE_TAG may not exist"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run migrations (unless skipped)
if [ "$SKIP_MIGRATIONS" != "skip" ]; then
    echo ""
    echo "Running database migrations..."
    if ! bin/run_spot_job.sh --staging $BACKEND_IMAGE_TAG migrate; then
        echo "Error: Migration failed!"
        read -p "Continue with deployment anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    echo ""
    echo "Collecting static files..."
    bin/run_spot_job.sh --staging $BACKEND_IMAGE_TAG collectstatic --no-input || true
fi

# Deploy Celery
echo ""
echo "Deploying Celery workers..."
cat kubernetes/celery.yml | envsubst | kubectl apply -n $NAMESPACE_ENV -f -

# Deploy Backend
echo ""
echo "Deploying backend application..."
cat kubernetes/ipno.yml | envsubst | kubectl apply -n $NAMESPACE_ENV -f -

echo ""
echo "================================================"
echo "  Deployment initiated!"
echo "================================================"
echo ""
echo "Monitor deployment status:"
echo "  kubectl get pods -n $NAMESPACE_ENV"
echo "  kubectl rollout status deployment/ipno-backend -n $NAMESPACE_ENV"
echo "  kubectl rollout status deployment/celery -n $NAMESPACE_ENV"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/ipno-backend -n $NAMESPACE_ENV"
echo "  kubectl logs -f deployment/celery -n $NAMESPACE_ENV"
echo ""
echo "Rollback if needed:"
echo "  kubectl rollout undo deployment/ipno-backend -n $NAMESPACE_ENV"
echo "  kubectl rollout undo deployment/celery -n $NAMESPACE_ENV"
echo ""
