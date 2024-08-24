
"""Quick snippet explaining how to set config options when using start_ipython."""

# First create a config object from the traitlets library
from traitlets.config import Config
import IPython

c = Config()

# Now we can set options as we would in a config file: 
#   c.Class.config_value = value
# For example, we can set the exec_lines option of the InteractiveShellApp
# class to run some code when the IPython REPL starts
c.InteractiveShellApp.exec_lines = [
    'from dotenv import load_dotenv',
    'load_dotenv()',
    'from langchain_community.graphs import Neo4jGraph',
    'from auto_resume.linked_in.linked_in import LinkedIn', 
    'import auto_resume.model as model',
    'from auto_resume.page import init_browser',
    'import prisma',
    'db = prisma.get_client()',
    'db.connect()',
    'model.Files.init()',
    'config = model.Config.load()'
]
c.InteractiveShell.colors = 'LightBG'
c.InteractiveShell.confirm_exit = False
c.TerminalIPythonApp.display_banner = False

# Now we start ipython with our configuration
IPython.start_ipython(config=c)


