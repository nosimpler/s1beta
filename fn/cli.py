# cli.py - routines for the command line interface console sssh.py
#
# v 1.4.2
# rev 2012-11-09 (SL: Added psth to qnd function)
# last major: (SL: Minor)

from cmd import Cmd
from datetime import datetime
import clidefs
# import plot.psummary as psum
import multiprocessing
import subprocess
import fileio as fio
import os, signal
import readline as rl
import paramrw
import itertools as it
from praster import praster
from ppsth import ppsth

# def handler(signum, frame):
#     print '\nKeyboardInterrupt'

class Console(Cmd):
    def __init__(self, file_input=""):
        Cmd.__init__(self)
        # signal.signal(signal.SIGINT, handler)
        self.prompt = '\033[93m' + "[s1] " + '\033[0m'
        self.intro  = "\nThis is the SomatoSensory SHell\n"
        self.droot = '/repo/data/s1'
        self.f_history = '.s1sh_history'
        self.ddate = []
        self.dlast = []
        self.dlist = []
        self.dir_data = []
        self.expmts = []
        self.file_input = file_input
        self.sim_list = []
        self.param_list = []
        self.var_list = []
        self.N_sims = 0

        self.nprocs = multiprocessing.cpu_count()

        # Create the initial datelist
        # self.datelist = get_subdir_list(self.droot)

        # set the date, grabs a dlist
        self.do_setdate(datetime.now().strftime("%Y-%m-%d"))

    def do_giddict(self, args):
        pass

    def do_open(self, args):
        """Attempts to open a new file of params
        """
        if os.path.isfile(args):
            self.file_input = args
            print "New file is:", self.file_input
        else:
            print "Does not appear to exist"
            return 0

    def do_diff(self, args):
        """Runs a diff on various data types
        """
        pass

    def do_quickdraw(self, args):
        self.do_setdate('2012-04-02')
        # self.do_setdate('cppub')
        self.do_load('gassembly-002')
        self.do_pcompare('sim0=11 sim1=11')

    def do_testls(self, args):
        # file_list = fio.file_match('../param', '*.param')
        print "dlist is:", self.dlist
        print "datelist is:", self.datelist
        print "expmts is:", self.expmts

    ## Command definitions ##
    def do_file(self, args):
        """Print .params file being read for simulations
        """
        print self.file_input

    def do_expmts(self, args):
        """Show list of experiments
        """

        if not len(self.expmts):
            print "Attempting to generate expmt list"
            self.expmts = gen_expmts(self.file_input)

        prettyprint(self.expmts)

    def do_vars(self, args):
        """Show variables in simulation and their values
        """
        self.do_expmts([])

        for var in self.var_list:
            print var[0]+":", var[1]

    def do_view(self, args):
        """Views the changes in the .params file. Use like 'load'
           but does not commit variables to workspace
        """
        # droot = '/repo/data/audtc'
        dcheck = os.path.join(self.droot, self.ddate, args)

        if os.path.exists(dcheck):
            # get a list of the .params files
            sim_list = fio.gen_sim_list(dcheck)
            expmts = gen_expmts(sim_list[0])
            var_list = changed_vars(sim_list)

            prettyprint(sim_list)
            prettyprint(expmts)
            for var in var_list:
                print var[0]+":", var[1]

    def complete_view(self, text, line, j0, J):
        """complete function for view
        """
        if text:
            x = [item for item in self.dlist if item.startswith(text)]
            if x:
                return x
            else:
                return 0
        else:
            return self.dlist

    def do_list(self, args):
        """Lists simulations on a given date
           'args' is a date
        """
        dcheck = os.path.join(self.droot, args)

        if os.path.exists(dcheck):
            dir_list = [name for name in os.listdir(dcheck) if os.path.isdir(os.path.join(dcheck, name))]
            prettyprint(dir_list)
        else:
            print "Cannot find directory"
            return 0

    def do_setdate(self, args):
        """Sets the date string to the specified date
        """
        dcheck = os.path.join(self.droot, args)

        if os.path.exists(dcheck):
            self.ddate = args
        else:
            self.ddate = 'cppub'

        print "Date set to", self.ddate
        
        # also get subdir list
        # somepath = os.path.join(self.droot, self.ddate)
        # self.dlist = get_subdir_list(os.path.join(somepath))

    def complete_setdate(self, text, line, j0, J):
        """complete function for setdate
        """
        if text:
            x = [item for item in self.datelist if item.startswith(text)]
            if x:
                return x
            else:
                return 0
        else:
            return self.datelist

    def do_checkdate(self, args):
        """Displays the current date
        """
        print self.ddate

    def do_load(self, args):
        """Load parameter file and regens all vars
        """
        dir_check = os.path.join(self.droot, self.ddate, args)

        if os.path.exists(dir_check):
            self.dir_data = dir_check
            self.simpaths = fio.SimulationPaths(self.dir_data)

        else:
            print dir_check
            print "Could not find that dir, maybe check your date?"
            return 0

    def complete_load(self, text, line, j0, J):
        """complete function for load
        """
        if text:
            x = [item for item in self.dlist if item.startswith(text)]
            if x:
                return x
            else:
                return 0
        else:
            return self.dlist

    def do_replot(self, args):
        """Regenerates plots in given directory
        """
        # regenerate_plots(self.dir_data)

        # simpaths.filelists is the list of files
        fparam = self.simpaths.filelists['param'][0]
        dfig_spk = self.simpaths.dfigs['spikes']

        # same for all spike rasters
        fext_figspk = self.simpaths.datatypes['figspk']

        pool = multiprocessing.Pool()
        for fparam, fspk in it.izip(self.simpaths.filelists['param'], self.simpaths.filelists['rawspk']):
            gid_dict, p = paramrw.read(fparam)
            pool.apply_async(praster, (gid_dict, p['tstop'], fspk, dfig_spk))

        pool.close()
        pool.join()

        fio.epscompress(dfig_spk, fext_figspk)

    def do_psth(self, args):
        # self.do_setdate('2012-11-07')
        # self.do_load('inhtone-001')
        ppsth(self.simpaths)

    def do_summary(self, args):
        epslist = fio.file_match(self.simpaths.dfigs['spikes'], '.eps')
        clidefs.pdf_create(self.dir_data, 'testing', epslist)

    def do_save(self, args):
        """Copies the entire current directory over to the cppub directory
        """
        copy_to_pub(self.dir_data)

    def do_runsim(self, args):
        """Run the simulation code
        """
        try:
            # self.expmts is the kain expmt subfolder
            cmd = ['mpiexec -n 4 ./s1run.py']
            # cmd = ['mpiexec -n %i ./s1run.py' % self.nprocs]
            proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            # self.do_load(self.dir_data)

        except (KeyboardInterrupt):
            print "Caught a break"

    def do_runpwr(self, args):
        exec_pwr(self.dir_data)

    def do_runrates(self, args):
        exec_rates(self.dir_data)

    def do_phist(self, args):
        """Create phase hist plot
        """
        exec_phist(self.dir_data, args)

    def do_pphase(self, args):
        """Create phase hist full plot
        """
        exec_pphase(self.dir_data, args)

    def do_pcompare3(self, args):
        """Plot compare 3
        """
        exec_pcompare3(self.dir_data, args)

    def do_plotvars(self, args):
        """Customizes plots
        """
        exec_plotvars(args, self.dir_data)

    def do_hist(self, args):
        """Print a list of commands that have been entered"""
        print self._hist

    def do_pwd(self, args):
        """Displays active dir_data"""
        print self.dir_data

    def do_ls(self, args):
        """Displays active param list"""
        prettyprint(self.param_list)

    # This is somewhat of a hack -- couldn't get multiple args working
    def do_show(self, args):
        """show: shows a list of params that starts with 'param' for simulation n
        """
        # print args
        vars = args.split(' in ')

        # print vars
        if len(vars) == 2:
            # split was successful
            s0 = vars[0].split()

            # print s0
            # try to split s0
            # s0_vars = s0.split()
            if len(s0) == 2:
                expmt = s0[0]
                prange = s0[1]
            else:
                print "Needs two arguments before ' in '"
                return 0

            # s1 is the sim number
            n = int(vars[1])
        else:
            # attempt to split by space
            s0 = vars[0].split()
            # print s0
            if len(s0) == 2:
                expmt = s0[0]
                prange = s0[1]

                # assume 0
                n = 0
            else:
                # assume first is expmt and try to proceed with changed
                expmt = s0[0]
                prange = 'changed'
                n = 0

        # Find the param list to traverse based on expmt
        if expmt in self.expmts:
            plist = [ex[1] for ex in self.param_list if ex[0] == expmt][0]
        else:
            print "No such experiment?"
            return 0

        # print plist
        # Search for params based on prange
        if prange == 'changed':
            # get the changed params and then print those values from the given simulation
            if n < self.N_sims:
                for line in self.var_list:
                    # Get the value of the param
                    with open(plist[n]) as f_params:
                        params = (param.rstrip() for param in f_params)
                        params = [param for param in params if param.startswith(line[0])]

                    print params[0]
            else:
                print "No such simulation"
                return 0

        elif prange == 'all':
            if n < self.N_sims:
                with open(plist[n]) as f_params:
                    lines = (line.rstrip() for line in f_params)
                    lines = [line for line in lines if line]

                prettyprint(lines)
            else:
                print "No such simulation"
                return 0

        else:
            if n < self.N_sims:
                with open(plist[n]) as f_params:
                    lines = (line.rstrip() for line in f_params)
                    lines = [line for line in lines if line.startswith(prange)]

                prettyprint(lines)
            else:
                print "No such simulation"
                return 0

    def complete_show(self, text, line, j0, J):
        """Completion function for show
        """
        if text:
            return [expmt for expmt in self.expmts if expmt.startswith(text)]
        else:
            return self.expmts

    def do_showf(self, args):
        """Show frequency information from rate files
        """
        vars = args.split(' in ')
        expmt = vars[0]
        n = int(vars[1])

        if n < self.N_sims:
            drates = os.path.join(self.dir_data, expmt, 'rates')
            ratefile_list = fio.file_match(drates, '*.rates')

            with open(ratefile_list[n]) as frates:
                lines = (line.rstrip() for line in frates)
                lines = [line for line in lines if line]

            prettyprint(lines)
        else:
            print "In do_showf in cli: out of range?"
            return 0

    def complete_showf(self, text, line, j0, J):
        """Completion function for showf
        """
        if text:
            return [expmt for expmt in self.expmts if expmt.startswith(text)]
        else:
            return self.expmts

    def do_Nsims(self, args):
        """Show number of simulations in each 'experiment'
        """
        print self.N_sims

    def do_pngv(self, args):
        """Attempt to find the PNGs and open them
        """
        if args == 'all':
            file_viewer(self.dir_data, 'all')
        else:
            # pretest to see if the experimental directory exists
            if not os.path.isdir(os.path.join(self.dir_data, args, 'spec')):
                print "Defaulting to first. Try one of: "
                prettyprint(self.expmts)
                expmt = os.path.join(self.dir_data, self.expmts[0])
            else:
                expmt = args

            file_viewer(self.dir_data, expmt)

    def complete_pngv(self, text, line, j0, J):
        if text:
            return [expmt for expmt in self.expmts if expmt.startswith(text)]
        else:
            return self.expmts

    ## Command definitions to support Cmd object functionality ##
    def do_exit(self, args):
        """Exits from the console
        """
        return -1

    def do_EOF(self, args):
        """Exit on system end of file character
        """
        return self.do_exit(args)

    def do_shell(self, args):
        """Pass command to a system shell when line begins with '!'
        """
        os.system(args)

    def do_help(self, args):
        """Get help on commands
           'help' or '?' with no arguments prints a list of commands for which help is available
           'help <command>' or '? <command>' gives help on <command>
        """
        ## The only reason to define this method is for the help text in the doc string
        Cmd.do_help(self, args)

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        Cmd.preloop(self)   ## sets up command completion
        self._hist    = self.load_history()
        self._locals  = {}      ## Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """Take care of any unfinished business.
           Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
        """
        self.write_history()
        Cmd.postloop(self)   ## Clean up command completion
        print "Exiting..."

    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modify the input line
            before execution (for example, variable substitution) do it here.
        """
        self._hist += [ line.strip() ]
        return line

    def postcmd(self, stop, line):
        """If you want to stop the console, return something that evaluates to true.
           If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):    
        """Do nothing on empty input line"""
        pass

    def default(self, line):       
        """Called on an input line when the command prefix is not recognized.
           In that case we execute the line as Python code.
        """
        try:
            if line == p[0]:
                print p[1]
            exec(line) in self._locals, self._globals
        except Exception, e:
            print e.__class__, ":", e

    # Function to read the history file
    def load_history(self):
        with open(self.f_history) as f_in:
            lines = (line.rstrip() for line in f_in)
            lines = [line for line in lines if line]

        return lines

    def history_remove_dupes(self):
        unique_set = set()
        return [x for x in self._hist if x not in unique_set and not unique_set.add(x)]

    # function to write the history file
    def write_history(self):
        # first we will clean the list of dupes
        unique_history = self.history_remove_dupes()
        with open(self.f_history, 'w') as f_out:
            for line in unique_history[-100:]:
                f_out.write(line+'\n')
