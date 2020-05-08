import os, subprocess
import requests
from kubespawner import KubeSpawner

class ModularSpawner(KubeSpawner):        
    def _options_form_default(self):
        """
        Generates html form to choose stacks from
        """
        
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

        # Generate html form
        return self.form

    def options_from_form(self, formdata):
        # Decode user choices        
        options = [True if formdata.get(option, None) else False for option in self.options]
        
        # Get image hash by running `polus-railyard` 
        tag = subprocess.run(('railyard hash ' + '-b ' + base + ' ' + ' '.join([f'-a {item}' for stack,included in zip(self.stacks,options) for item in stack if included])).split(' '), capture_output=True).stdout.decode("utf-8").rstrip()

        #Check if image exist to avoid PullErrors
        if requests.get('https://hub.docker.com/v2/repositories/labshare/polyglot-notebook/tags/' + tag).status_code != 200:
            #if image does not exist, switch to the maximal image with all stacks included
            self.log.debug("Requested tag %s is not in registry, using default image", tag)
            options = [True] * len(stacks)
            tag = subprocess.run(('railyard hash ' + '-b ' + base + ' ' + ' '.join([f'-a {item}' for stack,included in zip(stacks,options) for item in stack if included])).split(' '), capture_output=True).stdout.decode("utf-8").rstrip()
        
        # Get full image tag
        image = 'labshare/polyglot-notebook:' + tag

        setattr(self, 'image', image)
        return dict(profile={'display_name': 'Chosen image', 'default': True, 'kubespawner_override': {'image': image,}})

