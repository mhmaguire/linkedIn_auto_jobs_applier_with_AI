
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
    'from auto_resume.linked_in.linked_in import LinkedIn', 
    'from auto_resume.linked_in.job_search import JobSearchPage, JobScraper, JobPage',
    'from auto_resume.model.config import Files, Config',
    'from auto_resume.model.resume import MasterResume',
    'from auto_resume.model.job import Job',
    'from auto_resume.agent import resume',
    'from auto_resume.page import init_browser',
    'from prisma import Prisma',
    'db = Prisma(auto_register=True)',
    'await db.connect()',
    'Files.init()',
    'config = Config.load()',
    'resume_obj = MasterResume.load(Files.plain_text_resume_file)',
    # 'bot = Bot.configure(config, resume_obj, db)'
]
c.InteractiveShell.colors = 'LightBG'
c.InteractiveShell.confirm_exit = False
c.TerminalIPythonApp.display_banner = False

# Now we start ipython with our configuration
IPython.start_ipython(config=c)


