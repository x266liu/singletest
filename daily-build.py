import os, csv, sys, string, os
import traceback 
import ntpath
import subprocess
from subprocess import call
import shutil
import git



gitPath = "C:/Users/liuxu/Documents/OneDrive/文档/testffmpeg"
def daily_build(lst, gitPath):
	
	print("\n=============================================================")
	#changing directory
	os.chdir(gitPath)
	#git pull
	subprocess.call(["git", "pull"])
	repo = git.Repo(gitPath)
	master = repo.head.reference
	commitnum = master.commit.hexsha	
	print(commitnum)
	print("new")
	
	if(commitnum != lst):
		subprocess.call(["MSBuild.exe", "simplest_ffmpeg_player2.sln"])
	
	else:
		print("update to newest version")
		return(0)
	
	'''
	if os.path.getsize('/home/ssimwave/cwork/changes.txt')>0 :
		#delete the old version first
		if os.path.isdir("/home/ssimwave/cwork/ssim-test-linux/Bin/SQMLib/Linux"):
			shutil.rmtree("/home/ssimwave/cwork/ssim-test-linux/Bin/SQMLib/Linux")
			print("\n============= delete the old target folder ==================")
		
			#create the new folder
	'''		
	'''	
		os.chdir("/home/green/cwork/ssim-test-linux/bin/SSIMplusYUV")
		
		while 1:
			try:
				os.system("mkdir linux")
				break
			except OSError as e:
				if e.errno != 17:
					raise
				pass	
	'''
	'''
		# compile the project then, go to the directory first, we need move to the dest folder.
		os.chdir("/home/ssimwave/cwork/ssim/code/SPLCLI/build/linux/Release")
		
		#run compile command then,
		make_process = subprocess.Popen(["make","clean","all"], stderr=subprocess.STDOUT)
		if make_process.wait() != 0:
			something_went_wrong();
			
		
		fromdirectory= "/home/ssimwave/cwork/ssim/code/SPLCLI/bin/linux"
		todirectory= "/home/ssimwave/cwork/ssim-test-linux/Bin/SQMLib/Linux"
		todirectory2= "/home/ssimwave/cwork/ssim-test-linux/Scripts"
		
		#if os.path.isdir("/home/ssimwave/cwork/ssim-test-linux/bin/SSIMplusYUV/linux"):
		shutil.copytree(fromdirectory , todirectory, None)
		#shutil.copytree(fromdirectory , todirectory2, None)
		print("\n============= copy to the old target folder =================")
		os.chdir("/home/ssimwave/cwork/ssim-test-linux/Scripts")	
		#run python3 test_Runner.py -full.
		subprocess.call([sys.executable,'/home/ssimwave/cwork/ssim-test-linux/Scripts/test_Runner.py','-dev2'])
	'''

def is_git_repo(path):
	try:
		_ = git.Repo(path).git_dir
		return True
	except git.exc.InvalidGitRepositoryError:
		return False

if __name__ == "__main__":
	gitPath = "C:/Users/liuxu/Documents/OneDrive/文档/testffmpeg"
	#already git clone into this folder for testing
	if(is_git_repo(gitPath) == True):
		os.chdir(gitPath)
			
		repo = git.Repo(gitPath)
		master = repo.head.reference
		commitnum = master.commit.hexsha	
		print("old")
		print(commitnum)	
		daily_build( commitnum , gitPath)
	else:
		os.chdir(gitPath)
		subprocess.call(["git", ["clone", "https://github.com/kaizeng045/ffmpeg_mpd.git"] ])
		os.chdir("ffmpeg_mpd")
		gitPath = gitPath + "/ffmpeg_mpd"
		repo = git.Repo(gitPath)
		master = repo.head.reference
		commitnum = master.commit.hexsha	
		print("old")
		print(commitnum)	
		daily_build( commitnum, gitPath )		
		
	


