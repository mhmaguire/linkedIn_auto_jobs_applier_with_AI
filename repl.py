
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
    'from selenium.webdriver.common.by import By',
    'from main import Bot',
    'from linked_in.job_search import JobScraper, JobPage',
    'from model.config import Files, Config',
    'from model.resume import Resume',
    'from prisma import Prisma',
    'from agent import resume',
    'db = Prisma()',
    'await db.connect()',
    'Files.init()',
    'config = Config.load()',
    'resume_obj = Resume.load(Files.plain_text_resume_file)',
    # 'bot = Bot.configure(config, resume_obj, db)'
]
c.InteractiveShell.colors = 'LightBG'
c.InteractiveShell.confirm_exit = False
c.TerminalIPythonApp.display_banner = False

# Now we start ipython with our configuration
IPython.start_ipython(config=c)


