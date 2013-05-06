# cli.py - routines for the command line interface console s1sh.py
#
# v 1.7.51irec
# rev 2013-05-06 (SL: added temporary spec_current call)
# last major: (SL: minor)

from cmd import Cmd
from datetime import datetime
import clidefs
import ast, multiprocessing, os, signal, subprocess
import readline as rl
import itertools as it
import fileio as fio
import paramrw
import specfn
import dipolefn
from praster import praster
from ppsth import ppsth, ppsth_grid

import praw

class Console(Cmd):
    def __init__(self, file_input=""):
        Cmd.__init__(self)
        self.prompt = '\033[93m' + "[s1] " + '\033[0m'
        self.intro  = "\nThis is the SomatoSensory SHell\n"
        self.dproj = '/repo/data/s1'
        self.server_default = self.__check_server()
        self.f_history = '.s1sh_hist_local'
        self.ddate = ''
        self.dlast = []
        self.dlist = []
        self.dsim = []
        self.expmts = []
        self.sim_list = []
        self.param_list = []
        self.var_list = []
        self.N_sims = 0

        # check to see if file_input is legit
        if os.path.isfile(file_input):
            self.file_input = file_input
        else:
            # use a default
            self.file_input = 'param/debug.param'

        # get initial count of avail processors for subprocess/multiprocessing routines
        self.nprocs = multiprocessing.cpu_count()

        # Create the initial datelist
        self.datelist = clidefs.get_subdir_list(self.dproj)

        # create the initial paramfile list
        self.__get_paramfile_list()

        # set the date, grabs a dlist
        self.do_setdate(datetime.now().strftime("%Y-%m-%d"))

    # splits argstring in format of --opt0=val0 --opt1=val1
    def __split_args(self, args):
        # split based on space
        args_tmp = args.split(' ')

        # only take the args that start with -- and include a =
        args_opt = [arg for arg in args_tmp if arg.startswith('--')]
        args_opt = [arg for arg in args_opt if '=' in arg]

        # final output list of tuples (?) or lists of args and values
        arg_list = []

        # iterate through args
        for arg in args_opt:
            if arg:
                # append output to the final list
                arg_list.append(arg.split('='))
                # opt, val = arg.split('=')

        return arg_list

    def __check_server(self):
        f_server = os.path.join(self.dproj, '.server_default')

        if os.path.isfile(f_server):
            # read the file and set the default server
            lines_f = fio.clean_lines(f_server)

            # there should only be one thing in this file, so assume that's the server name
            return lines_f[0]
        else:
            return ''

    # create a list of parameter files
    def __get_paramfile_list(self):
        dparam_default = os.path.join(os.getcwd(), 'param')
        self.paramfile_list = [f for f in os.listdir(dparam_default) if f.endswith('.param')]

    def do_debug(self, args):
        """Qnd function to test other functions
        """
        self.do_setdate('2013-05-01')
        self.do_load('rec_i-025')
        # self.do_spec_current('')
        self.do_praw('')
        # self.do_pdipole('grid')
        # self.do_pngv('')
        # self.do_show('spike in (4, 0)')
        # self.do_calc_dipole_avg('')
        # self.do_pdipole('evaligned')
        # self.do_specmax('in (testing, 0, 4) on [0, 1000.]')
        # self.do_avgtrials('dpl')
        # self.do_replot('')
        # self.do_specanalysis('max_freq=50')
        # self.do_addalphahist('--xmin=0 --xmax=500')
        # self.do_avgtrials('dpl')
        # self.do_dipolemin('in (mu, 0, 2) on [400., 410.]')
        # self.epscompress('spk')
        # self.do_psthgrid()

    def do_spec_current(self, args):
        self.spec_current_tmp = clidefs.exec_spec_current(self.ddata)

    def do_praw(self, args):
        '''praw is a fully automated function to replace the dipole plots with aggregate dipole/spec/spikes plots. Usage:
           [s1] praw
        '''
        praw.praw(self.ddata)

    # update the dlist
    def __update_dlist(self):
        if os.path.exists(self.ddate):
            self.dlist = [d for d in os.listdir(self.ddate) if os.path.isdir(os.path.join(self.ddate, d))]

    def do_setdate(self, args):
        """Sets the date string to the specified date
        """
        if args:
            dcheck = os.path.join(self.dproj, args)

            if os.path.exists(dcheck):
                self.ddate = dcheck
            else:
                self.ddate = 'cppub'

        self.__update_dlist()

        print "Date set to", self.ddate

    def complete_setdate(self, text, line, j0, J):
        """complete function for setdate
        """
        if text:
            print text
            x = [item for item in self.datelist if item.startswith(text)]
            if x:
                return x
        else:
            return self.datelist

    def do_load(self, args):
        """Load parameter file and regens all vars
           Date needs to be set correctly for this to work. See 'help setdate'
           Usage example:
           [s1sh] setdate 2013-01-01
           [s1sh] load mucomplex-000
        """
        # dir_check is the attempt at creating this directory
        dir_check = os.path.join(self.dproj, self.ddate, args)

        # check existence of the path
        if os.path.exists(dir_check):
            # create blank ddata structure from SimPaths
            self.ddata = fio.SimulationPaths()

            # set dsim after using ddata's readsim method
            self.dsim = self.ddata.read_sim(self.dproj, dir_check)
            self.p_exp = paramrw.ExpParams(self.ddata.fparam)
            print self.ddata.fparam
            self.var_list = paramrw.changed_vars(self.ddata.fparam)

        else:
            print dir_check
            print "Could not find that dir, maybe check your date?"

    def complete_load(self, text, line, j0, J):
        """complete function for load
        """
        if text:
            return [item for item in self.dlist if item.startswith(text)]

        else:
            return self.dlist

    def do_sync(self, args):
        """Sync with specified remote server. If 'exclude' is unspecified, by default will use the exclude_eps.txt file in the data dir. If exclude is specified, it will look in the root data dir. Usage examples:
           [s1] sync 2013-03-25
           [s1] sync 2013-03-25 --exclude=somefile.txt
        """
        try:
            fshort_exclude = ''
            list_args = args.split('--')

            # expect first arg to be the dsubdir
            dsubdir = list_args.pop(0)

            for arg in list_args:
                if arg:
                    opt, val = arg.split('=')

                    if opt == 'exclude':
                        fshort_exclude = val

            if not self.server_default:
                server_remote = raw_input("Server address: ")
            else:
                server_remote = self.server_default
                print "Attempting to use default server ..."

            # run the command
            if fshort_exclude:
                clidefs.exec_sync(self.dproj, server_remote, dsubdir, fshort_exclude)
            else:
                clidefs.exec_sync(self.dproj, server_remote, dsubdir)

            # path
            newdir = os.path.join('from_remote', dsubdir)
            self.do_setdate(newdir)

        except:
            print "Something went wrong here."

    def do_giddict(self, args):
        pass

    def do_specmax(self, args):
        """Find the max spectral power, report value and time.
           Usage: specmax in (<expmt>, <simrun>, <trial>) on [interval]
        """
        # look for first keyword
        if args.startswith("in"):
            try:
                # split by 'in' to get the interval
                s = args.split(" on ")

                # values are then in first part of s
                # yeah, this is gross, sorry. just parsing between parens for params
                expmt_group, n_sim_str, n_trial_str = s[0][s[0].find("(")+1:s[0].find(")")].split(", ")
                n_sim = int(n_sim_str)
                n_trial = int(n_trial_str)

                t_interval = ast.literal_eval(s[-1])
                clidefs.exec_specmax(self.ddata, expmt_group, n_sim, n_trial, t_interval)

            except ValueError:
                self.do_help('specmax')

        else:
            self.do_help('specmax')

    def do_dipolemin(self, args):
        """Find the minimum of a particular dipole
           Usage: dipolemin in (<expmt>, <simrun>, <trial>) on [interval]
        """
        # look for first keyword
        if args.startswith("in"):
            try:
                # split by 'in' to get the interval
                s = args.split(" on ")

                # values are then in first part of s
                # yeah, this is gross, sorry. just parsing between parens for params
                expmt_group, n_sim_str, n_trial_str = s[0][s[0].find("(")+1:s[0].find(")")].split(", ")
                n_sim = int(n_sim_str)
                n_trial = int(n_trial_str)

                t_interval = ast.literal_eval(s[-1])
                clidefs.exec_dipolemin(self.ddata, expmt_group, n_sim, n_trial, t_interval)

            except ValueError:
                self.do_help('dipolemin')

        else:
            self.do_help('dipolemin')

    def do_file(self, args):
        """Attempts to open a new file of params
        """
        if not args:
            print self.file_input
        elif os.path.isfile(args):
            self.file_input = args
            print "New file is:", self.file_input
        else:
            # try searching specifcally in param dir
            f_tmp = os.path.join('param', args)
            if os.path.isfile(f_tmp):
                self.file_input = f_tmp
            else:
                print "Does not appear to exist"
                return 0

    # tab complete rules for file
    def complete_file(self, text, line, j0, J):
        return [item for item in self.paramfile_list if item.startswith(text)]

    def do_diff(self, args):
        """Runs a diff on various data types
        """
        pass

    def do_testls(self, args):
        # file_list = fio.file_match('../param', '*.param')
        print "dlist is:", self.dlist
        print "datelist is:", self.datelist
        print "expmts is:", self.expmts

    def do_expmts(self, args):
        """Show list of experiments for active directory.
        """
        try:
            clidefs.prettyprint(self.ddata.expmt_groups)
        except AttributeError:
            self.do_help('expmts')
            print "No active directory?"

    def do_vars(self, args):
        """Show changed variables in loaded simulation and their values. Usage:
           [s1] vars
        """
        print "\nVars changed in this simulation:"

        # iterate through params and print them raw
        for var in self.var_list:
            print "  %s: %s" % (var[0], var[1])

        # cheap newline
        print ""

    # this is an old function obsolete for this project
    def do_view(self, args):
        """Views the changes in the .params file. Use like 'load'
           but does not commit variables to workspace
        """
        dcheck = os.path.join(self.dproj, self.ddate, args)

        if os.path.exists(dcheck):
            # get a list of the .params files
            sim_list = fio.gen_sim_list(dcheck)
            expmts = gen_expmts(sim_list[0])
            var_list = changed_vars(sim_list)

            clidefs.prettyprint(sim_list)
            clidefs.prettyprint(expmts)
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
        if not args:
            dcheck = os.path.join(self.dproj, self.ddate)

        else:
            dcheck = os.path.join(self.dproj, args)

        if os.path.exists(dcheck):
            self.__update_dlist()

            # dir_list = [name for name in os.listdir(dcheck) if os.path.isdir(os.path.join(dcheck, name))]
            clidefs.prettyprint(self.dlist)

        else:
            print "Cannot find directory"
            return 0

    def do_pngoptimize(self, args):
        """Optimizes png figures based on current directory
        """
        fio.pngoptimize(self.simpaths.dsim)

    def do_avgtrials(self, args):
        """Averages raw data over all trials for each simulation.
           Usage:
           [s1] avgtrials <datatype>
           where <datatype> is either dpl or spec
        """
        if not args:
            print "You did not specify whether to avgerage dpl or spec data. Try again."

        else:
            datatype = args
            clidefs.exec_avgtrials(self.ddata, datatype)

    def do_specanalysis(self, args):
        """Regenerates spec data and saves it to proper expmt directories. Usage:
           Can pass arguments to set max_freq, tstart, and tstop of analysis
           Args must be passed in form arg1=val, arg2=val, arg3=val
           Can pass any combination/permutation of args or no args at all
        """
        # preallocate variables so they always exist
        max_freq = None
        tstart = None
        tstop = None

        # Parse args if they exist
        if args:
            arg_list = args.split(', ')

            # Assign value to above variables if the value exists as input
            for arg in arg_list:
                if arg.startswith('max_freq'):
                    max_freq = float(arg.split('=')[-1])

                else:
                    print "Did not recognize argument. Not doing anything with it" 

                # elif arg.startswith('tstart'):
                #     tstart = float(arg.split('=')[-1])
 
                # elif arg.startswith('tstop'):
                #     tstop = float(arg.split('=')[-1])

        self.spec_results = clidefs.regenerate_spec_data(self.ddata, max_freq)

    def do_freqpwr(self, args):
        """Averages spec power over time and plots freq vs power. Fn can act per expmt or over entire simulation. If maxpwr supplied as arg, also plots freq at which max avg pwr occurs v.s input freq
        """
        if args == 'maxpwr':
            clidefs.freqpwr_analysis(self.ddata, self.dsim, maxpwr=1)

        else:
            clidefs.freqpwr_analysis(self.ddata, self.dsim, maxpwr=0)

    def do_freqpwrwithhist(self, args):
        clidefs.freqpwr_with_hist(self.ddata, self.dsim)

    def do_calc_dipole_avg(self, args):
        """Calculates average dipole using dipolefn.calc_avgdpl_stimevoked:
           Usage: [s1] calc_dipole_avg
        """
        dipolefn.calc_avgdpl_stimevoked(self.ddata)

    def do_pdipole(self, args):
        """Regenerates plots in given directory. Usage:
           To run on current working directory and regenerate each individual plot: 'pdipole'
           To run aggregates for all simulations (across all trials/conditions) in a directory: 'pdipole exp'
           To run aggregates with lines marking evoked times, run: 'pdipole evoked'
        """
        # temporary arg split
        arg_tmp = args.split(' ')

        # list of acceptable runtypes
        runtype_list = [
            'exp',
            'exp2',
            'evoked',
            'evaligned',
            'avg',
            'grid',
        ]

        # minimal checks in this function
        # assume that no ylim argument was specified
        if len(arg_tmp) == 1:
            runtype = arg_tmp[0]
            ylim = []

        else:
            # set the runtype to the first
            if arg_tmp[0] in runtype_list:
                runtype = arg_tmp[0]

            # get the list of optional args
            arg_list = self.__split_args(args)

            # default values for various params
            # i_ctrl = 0
            for opt, val in arg_list:
                # currently not being used
                if opt == 'i_ctrl':
                    i_ctrl = int(val)

            # assume the first arg is correct, split on that
            # arg_ylim_tmp = args.split(runtype)

            # if len(arg_ylim_tmp) == 2:
            #     ylim_read = ast.literal_eval(arg_ylim_tmp[-1].strip())
            #     ylim = ylim_read

            # else:
            #     ylim = []

        if runtype == 'exp':
            # run the avg dipole per experiment (across all trials/simulations)
            # using simpaths (ddata)
            dipolefn.pdipole_exp(self.ddata, ylim)

        elif runtype == 'exp2':
            dipolefn.pdipole_exp2(self.ddata)
            # dipolefn.pdipole_exp2(self.ddata, i_ctrl)

        elif runtype == 'evoked':
            # add the evoked lines to the pdipole individual simulations
            clidefs.exec_pdipole_evoked(self.ddata, ylim)

        elif runtype == 'evaligned':
            dipolefn.pdipole_evoked_aligned(self.ddata)

        elif runtype == 'avg':
            # plot average over all TRIALS of a param regime
            # requires that avg dipole data exist
            clidefs.exec_plotaverages(self.ddata, ylim)

        elif runtype == 'grid':
            dipolefn.pdipole_grid(self.ddata)

    def do_replot(self, args):
        """Regenerates plots in given directory. Usage:
           Can pass arguments to set xmin and xmax of plots
           Args must be passed in form --xmin=val --xmax=val
           Can pass none, one, or both args in any order
        """
        # preallocate variables so they always exist
        xmin = 0.
        xmax = 'tstop'

        # Parse args if they exist
        if args:
            arg_list = [arg for arg in args.split('--') if arg is not '']

            # Assign value to above variables if the value exists as input
            for arg in arg_list:
                if arg.startswith('xmin'):
                    xmin = float(arg.split('=')[-1])
 
                elif arg.startswith('xmax'):
                    xmax = float(arg.split('=')[-1])

                else:
                    print "Did not recognize argument %s. Not doing anything with it" % arg

            # Check to ensure xmin less than xmax
            if xmin and xmax:
                if xmin > xmax:
                    print "xmin greater than xmax. Defaulting to sim parameters"
                    xmin = 0.
                    xmax = 'tstop'

        # check for spec data, create it if didn't exist, and then run the plots
        clidefs.regenerate_plots(self.ddata, [xmin, xmax])

    def do_addalphahist(self, args):
        """Adds histogram of alpha feed input times to dpl and spec plots. Usage:
           [s1] addalphahist {--xmin=0 --xmax=100}
        """
        # preallocate variables so they always exist
        xmin = 0.
        xmax = 'tstop'

        # Parse args if they exist
        if args:
            arg_list = [arg for arg in args.split('--') if arg is not '']

            # Assign value to above variables if the value exists as input
            for arg in arg_list:
                if arg.startswith('xmin'):
                    xmin = float(arg.split('=')[-1])
 
                elif arg.startswith('xmax'):
                    xmax = float(arg.split('=')[-1])

                else:
                    print "Did not recognize argument %s. Not doing anything with it" %arg

            # Check to ensure xmin less than xmax
            if xmin and xmax:
                if xmin > xmax:
                    print "xmin greater than xmax. Defaulting to sim parameters"
                    xmin = 0.
                    xmax = 'tstop'

        clidefs.exec_addalphahist(self.ddata, [xmin, xmax])

    def do_aggregatespec(self, args):
        """Creates aggregates all spec data with histograms into one massive fig.
           Must supply column label and row label as --row_label:param --column_label:param"
           row_label should be param that changes only over experiments
           column_label should be a param that changes trial to trial
        """
        arg_list = [arg for arg in args.split('--') if arg is not '']
        print arg_list

        # Parse args
        for arg in arg_list:
            if arg.startswith('row'):
                row_label = arg.split(':')[-1]

                # See if a list is being passed in
                if row_label.startswith('['):
                    row_label = arg.split('[')[-1].split(']')[0].split(', ')

                else:
                    row_label = arg.split(':')[-1].split(' ')[0]

            elif arg.startswith('column'):
                column_label = arg.split(':')[-1].split(' ')[0]

            else:
                print "Did not recongnize argument. Going to break now."

        clidefs.exec_aggregatespec(self.ddata, [row_label, column_label])

    def do_plotaverages(self, args):
        """Creates plots of averaged dipole or spec data. Automatically checks if data exists. Usage:
           'plotaverages'
        """

        clidefs.exec_plotaverages(self.ddata)

    def do_epscompress(self, args):
        """Runs the eps compress utils on the specified fig type (currently either spk or spec)
        """
        for expmt_group in self.ddata.expmt_groups:
            if args == 'figspk':
                d_eps = self.ddata.dfig[expmt_group]['figspk']
            elif args == 'figspec':
                d_eps = self.ddata.dfig[expmt_group]['figspec']

            try:
                fio.epscompress(d_eps, '.eps')
            except UnboundLocalError:
                print "oy, this is embarrassing."

    def do_psthgrid(self, args):
        """Aggregate plot of psth
        """
        ppsth_grid(self.simpaths)

    # def do_psth(self, args):
    #     # self.do_setdate('2012-11-07')
    #     # self.do_load('inhtone-001')
    #     ppsth(self.simpaths)

    # def do_summary(self, args):
    #     epslist = fio.file_match(self.simpaths.dfigs['spikes'], '.eps')
    #     clidefs.pdf_create(self.dsim, 'testing', epslist)

    def do_save(self, args):
        """Copies the entire current directory over to the cppub directory
        """
        copy_to_pub(self.dsim)

    def do_runsim(self, args):
        """Run the simulation code
        """
        try:
            cmd_list = []
            cmd_list.append('mpiexec -n %i ./s1run.py %s' % (self.nprocs, self.file_input))

            for cmd in cmd_list:
                subprocess.call(cmd, shell=True)

        except (KeyboardInterrupt):
            print "Caught a break"

    def do_runpwr(self, args):
        exec_pwr(self.dsim)

    def do_runrates(self, args):
        exec_rates(self.dsim)

    def do_phist(self, args):
        """Create phase hist plot
        """
        exec_phist(self.dsim, args)

    def do_pphase(self, args):
        """Create phase hist full plot
        """
        exec_pphase(self.dsim, args)

    def do_pcompare3(self, args):
        """Plot compare 3
        """
        exec_pcompare3(self.dsim, args)

    def do_plotvars(self, args):
        """Customizes plots
        """
        exec_plotvars(args, self.dsim)

    def do_hist(self, args):
        """Print a list of commands that have been entered"""
        print self._hist

    def do_pwd(self, args):
        """Displays active dir_data"""
        print self.dsim

    def do_ls(self, args):
        """Displays active param list"""
        clidefs.prettyprint(self.param_list)

    def do_show(self, args):
        """show: shows a list of params that starts with 'param' for simulation n
           Usage: show <expmt> in (<N>, <N_T>)
           where <expmt> is one of the experimental groups,
                 <N> is the sim number, and <N_T> is the trial number
        """
        key_dict = self.p_exp.get_key_types()
        # print self.p_exp.N_sims, self.p_exp.N_trials

        # print args
        vars = args.split(' in ')
        expmt_group = vars[0]
        # expmt, search_str = vars[0].split(' ')

        # check to see if the expmt_group is valid
        if expmt_group not in self.ddata.expmt_groups:
            print "Perhaps not a valid experiment? Try:"
            print self.ddata.expmt_groups
            return 0

        # now get the tuple representing the N and N_T
        try:
            N, N_T = ast.literal_eval(vars[-1])
        except:
            print "Confused?"
            return 0

        # will we always be making up for this
        if not self.p_exp.N_trials:
            N_trials = 1
        else:
            N_trials = 0

        # check to make sure both sim and trial exist
        if (N < self.p_exp.N_sims) and (N_T < N_trials):
        # if (N < self.p_exp.N_sims) and (N_T < self.p_exp.N_trials):
            # create the filename
            fname_short = self.p_exp.trial_prefix_str % (N, N_T) + '-param.txt'
            fname = os.path.join(self.ddata.dfig[expmt_group]['param'], fname_short)

            if os.path.isfile(fname):
                print fname

            gid_dict, p = paramrw.read(fname)
            print "\nChanged vars and some standard vars:"
            for var in self.var_list:
                print "  %s:" % var[0], p[var[0]]

            # print some additional info
            list_meta = [
                'Trial',
                'N_pyr_x',
                'N_pyr_y',
            ]
            # print p.keys()
            for key in list_meta:
                if key in p.keys():
                    print "  %s:" % key, p[key]

            print ""
        else:
            print "Either N or N_T might be incorrect"
            # print N, N_T
            # print self.p_exp.N_sims, self.p_exp.N_trials
            return 0
            # print dir(self.p_exp)
            # print dir(self.ddata)
            # print self.p_exp.trial_prefix_str
            # print self.ddata.dfig
        # j_exp = int(vars[-1])
        # print expmt, search_str, j_exp

        # if expmt in self.ddata.expmt_groups:
        #     if search_str == 'changed':
        #         p_sim = self.p_exp.return_pdict(expmt, j_exp)
        #         for key in key_dict['dynamic_keys']:
        #             print "%s: %4.5f" % (key, p_sim[key])

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
            drates = os.path.join(self.dsim, expmt, 'rates')
            ratefile_list = fio.file_match(drates, '*.rates')

            with open(ratefile_list[n]) as frates:
                lines = (line.rstrip() for line in frates)
                lines = [line for line in lines if line]

            clidefs.prettyprint(lines)
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
        # assume args is an experiment
        if not args:
            # try the first of them
            expmt_group = self.ddata.expmt_groups[0]
        else:
            expmt_group = args

        if expmt_group not in self.ddata.expmt_groups:
            print "Try one of these:"
            print self.ddata.expmt_groups
            return 0

        else:
            # for now do just figdpl
            dimg = os.path.join(self.ddata.dsim, expmt_group, 'figdpl')
            clidefs.png_viewer_simple(dimg)

        # if args == 'all':
        #     clidefs.file_viewer(self.dsim, 'all')
        # else:
        #     # pretest to see if the experimental directory exists
        #     if not os.path.isdir(os.path.join(self.dsim, args, 'spec')):
        #         print "Defaulting to first. Try one of: "
        #         clidefs.prettyprint(self.expmts)
        #         expmt = os.path.join(self.dsim, self.expmts[0])
        #     else:
        #         expmt = args

        #     file_viewer(self.dsim, expmt)

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
