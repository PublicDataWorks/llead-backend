from django.core.management import call_command
from django.test import TestCase

from data.models import WrglRepo
from data.constants import WRGL_REPOS_DEFAULT


class CreateInitialWRGLReposCommandTestCase(TestCase):
    def test_call_command(self):
        call_command('create_initial_wrgl_repos')
        wrgl_repo_objects = WrglRepo.objects.all()
        assert wrgl_repo_objects.count() == len(WRGL_REPOS_DEFAULT)

        for wrgl_repo_data in WRGL_REPOS_DEFAULT:
            wrgl_repo_object = wrgl_repo_objects.filter(repo_name=wrgl_repo_data['repo_name']).first()
            assert wrgl_repo_object
            assert wrgl_repo_object.data_model == wrgl_repo_data['data_model']
