import os, time, argparse
from datetime import timedelta

log_inf_name = 'clean_old.inf.log'
log_err_name = 'clean_old.err.log'

def log_print(lvl, *fargs):
	global args, fe, fi
	if lvl > args.verbosity: return
	tm = time.ctime(time.time())
	fargs = [tm] + list(fargs)
	if lvl == 0: 
		fargs = ['ERROR:'] + list(fargs)
		if fe: fe.write(' '.join(fargs) + '\n')
	print(*fargs)
	if fi: fi.write(' '.join(fargs) + '\n')

def delete_if_time_has_come(name):
	global args
	statinfo = os.lstat(name)
	ftime=statinfo.st_atime
	diff_days = timedelta(0, curr_time - ftime).days
	log = '{0} | {1} | {2}'.format(name, time.ctime(ftime), diff_days)
	if os.path.isfile(name): 
		if diff_days > args.days:
			log_print(1, log, '|', 'removing...')
			if not args.directory in name: raise ValueError('Somehow left working directory! Check parameters carefully!')
			if args.trial: return
			try: os.remove(name)
			except PermissionError: log_print(0, 'Acess denied')
		else: log_print(2, log, '|', 'skipping...')
	else: 
		if args.trial: return
		try: os.rmdir(name)
		except OSError: pass
		except PermissionError: 
			log_print(0, log, '|', 'removing directory...')
			log_print(0, 'Acess denied')

# Entry point
curr_time = time.time()
parser = argparse.ArgumentParser(description='Deletes files with last access date earlier than <days> ago in <directory>')
parser.add_argument('directory', help='directory to delete files from')
parser.add_argument('days', type=int, help='period in days')
parser.add_argument('-l', '--logs', metavar='<DIR>', default='', help='Log directory, no logs if not given')
parser.add_argument('-t', '--trial', action='store_const', const=True, default=False, help='don\'t really delete files, logging only')
parser.add_argument('-v', '--verbosity', metavar='<N>', type=int, default=0, help='0 (default): errors only, 2: all messages' )
args = parser.parse_args()
fi = fe = None
if args.logs:
	if not os.path.exists(args.logs): os.makedirs(args.logs)
	fi = open( os.path.join(args.logs, log_inf_name), 'a')
	fe = open( os.path.join(args.logs, log_err_name), 'a')
log_print(1, 'Starting at', time.ctime(curr_time))
for root, dirs, files in os.walk(args.directory, topdown=False):
	for name in files: delete_if_time_has_come(os.path.join(root, name))
	for name in dirs:  delete_if_time_has_come(os.path.join(root, name))
if hasattr(fe, 'close'): fe.close()
if hasattr(fi, 'close'): fi.close()
