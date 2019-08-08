import os
from subprocess import call

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Compiles Handlebars template files into a precompiled JS file'

    def add_arguments(self, parser):
        parser.add_argument('-o',
                            default=os.path.join(settings.BASE_DIR, 'wildlifelicensing', 'static', 'wl', 'js', 'precompiled_handlebars_templates.js'),
                            help='output file')

        parser.add_argument('-p', default='handlebars_templates', help='Handlebars template root directory')

    def handle(self, *args, **options):
        handlebars_templates = []

        for app in settings.INSTALLED_APPS:
            directory_args = [settings.BASE_DIR] + app.split('.') + [options['p']]
            app_handlebars_templates_path = os.path.join(*directory_args)
            if os.path.isdir(app_handlebars_templates_path):
                for handlebars_template in os.listdir(app_handlebars_templates_path):
                    handlebars_templates.append(os.path.join(app_handlebars_templates_path, handlebars_template))

        args = ['handlebars', '-a', '-m'] + handlebars_templates + ['-f', options['o']]

        call(args)
