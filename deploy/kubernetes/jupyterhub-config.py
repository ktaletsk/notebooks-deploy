import os,sys,subprocess
import requests
from oauthenticator.generic import LocalGenericOAuthenticator
from kubespawner import KubeSpawner

class DemoFormSpawner(KubeSpawner):
    def __init__(self):
        self.stacks_path = '/stacks'

        # Filename for the base stack pasted from Jenkins pipeline
        self.base = 'BASE_STACK_VALUE'

        # Groups of stacks filenames and their names are pasted from Jenkins pipeline
        # Format:
        #   self.stacks = [['stack1.yaml', 'stack2.yaml'], ['stack3.yaml'], ['stack4.yaml']]
        #   self.stacks_names = ['Name A', 'Name B', 'Name C']
        # Lengths of self.stacks and self.stacks_names must be the same
        self.stacks = STACKS_VALUE
        self.stacks_names = STACKS_NAMES_VALUE
        
        # Prepend path to stacks folder
        self.base = os.path.join(self.stacks_path, self.base)
        self.stacks = [[os.path.join(self.stacks_path, s) for s in stack] for stack in self.stacks]

        self.options = [f'option{i+1}' for i in range(len(stacks))]
        
        self.form = """
<div class="form-group">
    Choose language kernels and/or packages:
    <br>"""
        
        for i in range(len(stacks)):
            self.form +=(f"""
    <input type="checkbox" id="option{i+1}" name="option{i+1}">
    <label for="option1">{self.stacks_names[i]}</label><br>""")
        
        self.form += """
</div>"""

    def _options_form_default(self):
        # Generate html form
        return self.form

    def options_from_form(self, formdata):
        # Decode user choices        
        options = [True if formdata.get(option, None) else False for option in self.options]
        
        # Get image hash by running `polus-railyard` 
        tag = subprocess.run(('railyard hash ' + '-b ' + base + ' ' + ' '.join([f'-a {item}' for stack,included in zip(self.stacks,options) for item in stack if included])).split(' '), capture_output=True).stdout.decode("utf-8").rstrip()
        
        # Get full image tag
        image = 'labshare/polyglot-notebook:' + tag

        #Check if image exist to avoid PullErrors
        if requests.get('https://hub.docker.com/v2/repositories/labshare/polyglot-notebook/tags/' + tag).status_code != 200:
            #if image does not exist, switch to the maximal image with all stacks included
            self.log.debug("Requested image %s is not in registry, using default image", image)
            options = [True] * len(stacks)
            tag = subprocess.run(('railyard hash ' + '-b ' + base + ' ' + ' '.join([f'-a {item}' for stack,included in zip(stacks,options) for item in stack if included])).split(' '), capture_output=True).stdout.decode("utf-8").rstrip()
            image = 'labshare/polyglot-notebook:' + tag
            
        setattr(self, 'image', image)
        return dict(profile={'display_name': 'Chosen image', 'default': True, 'kubespawner_override': {'image': image,}})

c = get_config()
c.JupyterHub.spawner_class = DemoFormSpawner
c.DemoFormSpawner.start_timeout=1000

# Which container to spawn
c.DemoFormSpawner.default_url = '/lab'
c.DemoFormSpawner.uid = 1000 #uid 1000 corresponds to jovyan, uid 0 to root
c.DemoFormSpawner.cmd = ['jupyter-labhub']
c.DemoFormSpawner.working_dir = '/home/jovyan'
c.DemoFormSpawner.service_account='jupyteruser-sa'

# Per-user storage configuration
c.DemoFormSpawner.pvc_name_template = 'claim-{username}'
c.DemoFormSpawner.storage_class = 'STORAGE_CLASS_VALUE'
c.DemoFormSpawner.storage_capacity = 'STORAGE_PER_USER_VALUE'
c.DemoFormSpawner.storage_access_modes = ['ReadWriteOnce']
c.DemoFormSpawner.storage_pvc_ensure = True

# Volumes to attach to Pod
c.DemoFormSpawner.volumes = [
    {
        'name': 'volume-{username}',
        'persistentVolumeClaim': {
            'claimName': 'claim-{username}'
        }
    },
    {
        'name': 'shared-volume',
        'persistentVolumeClaim': {
            'claimName': 'notebooks-pv-claim'
        }
    },
    {
        'name': 'wipp-volume',
        'persistentVolumeClaim': {
            'claimName': 'WIPP_STORAGE_PVC_VALUE'
        }
    }
]

# Where to mount volumes
c.DemoFormSpawner.volume_mounts = [
    {
        'mountPath': '/home/jovyan/work',
        'name': 'volume-{username}'
    },
    {
        'mountPath': '/opt/shared/notebooks',
        'name': 'shared-volume'
    },
    {
        'mountPath': '/opt/shared/wipp',
        'name': 'wipp-volume'
    }
]

c.JupyterHub.allow_named_servers=True
c.JupyterHub.ip='0.0.0.0'
c.JupyterHub.hub_ip='0.0.0.0'

# Required for AWS
c.JupyterHub.hub_connect_ip='jupyterhub-internal'

c.JupyterHub.cleanup_servers=False
# c.ConfigurableHTTPProxy.should_start=False
c.JupyterHub.cookie_secret_file = '/srv/jupyterhub/jupyterhub_cookie_secret'

OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
ADMIN_USERS = os.getenv('ADMIN_USERS')

c.JupyterHub.authenticator_class = LocalGenericOAuthenticator

c.Authenticator.admin_users = set(ADMIN_USERS.split(';'))

c.LocalGenericOAuthenticator.client_id = OAUTH_CLIENT_ID
c.LocalGenericOAuthenticator.client_secret = OAUTH_CLIENT_SECRET
c.LocalGenericOAuthenticator.username_key = "email"
c.LocalGenericOAuthenticator.userdata_method = "GET"
c.LocalGenericOAuthenticator.extra_params = dict(client_id=OAUTH_CLIENT_ID, client_secret=OAUTH_CLIENT_SECRET)
c.LocalGenericOAuthenticator.basic_auth = False
c.LocalGenericOAuthenticator.create_system_users = True
c.LocalGenericOAuthenticator.add_user_cmd = ['adduser', '-q', '--gecos', '""', '--disabled-password', '--force-badname']
c.LocalGenericOAuthenticator.auto_login = True

# Set up WIPP UI url for integration with WIPP
c.DemoFormSpawner.environment = {
    'WIPP_UI_URL': 'WIPP_UI_VALUE',
    'WIPP_API_INTERNAL_URL': 'WIPP_API_INTERNAL_VALUE',
    'WIPP_NOTEBOOKS_PATH': 'WIPP_NOTEBOOKS_PATH_VALUE'
}

# Service to shutdown inactive Notebook servers after --timeout seconds
c.JupyterHub.services = [
    {
        'name': 'cull-idle',
        'admin': True,
        'command': [sys.executable, '/srv/jupyterhub/config/cull-idle-servers.py', '--timeout=3600'],
    }
]