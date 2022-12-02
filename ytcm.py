try:
    import subprocess
    import pytube
    import glob
    import sys
    import os
    from awesome_progress_bar import ProgressBar
    import random
    import shutil
    import platform
    YSIZE = os.get_terminal_size()[0]
except ImportError:
    print("FATAL ERROR: Some modules could not be found.")
    sys.exit(1)
if platform.system() != "Windows":
    sfs = "/"
else:
    sfs = "\\"
try:
    args = sys.argv[1:]
    if len(args) == 0 or (args[0][0:24] != "https://www.youtube.com/" and "-d" not in args and "--help" not in args and not "--empty" in args):
        raise IndexError("ERROR")
    if "--help" in args:
        print("Youtube Compilation Maker v0.2 (c) 2022 Enderbyte Programs LLC")
        print("--help      : Show this menu")
        print("-d          : Does not download videos, only extracts and compiles")
        print("-c          : Does not compile videos, only downloads (using in conjunction with -d will recompile files)")
        print("--nowaste   : Cleans up extra files at the end of session")
        print("--clean     : Clean files before downloading/compiling")
        print("--cleanc    : Clean extracted files only (useful in conjunction with -d)")
        print("--empty     : Empty files then exit")
        sys.exit()
    if "-d" in args:
        _dlv = False
    else:
        _dlv = True
    if "-c" in args:
        _exv = False
    else:
        _exv = True
    
except IndexError:
    print("ERROR: Please provide url to channel (eg. python3 ytdn.py <channel url> <args (optional)>) or run with --help for help")
    sys.exit()

rsz = subprocess.run(["ffmpeg"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if rsz.returncode != 0 and rsz.returncode != 1:
    print("Did you forget to install ffmpeg?")
    sys.exit(1)

if "--clean" in args:
    [os.remove(l) for l in glob.glob("*.mp4")+glob.glob("*.txt")]#I love python
elif "--cleanc" in args:
    [os.remove(l) for l in glob.glob("*s.mp4")+glob.glob("*x.mp4")+glob.glob("*.txt")+glob.glob("*t.mp4")]
elif "--empty" in args:
    [os.remove(l) for l in glob.glob("*.mp4")+glob.glob("*.txt")]
    sys.exit()

def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)


if _dlv:# Only downloading when conditional. Downloading takes over an hour.
    c = pytube.Channel(args[0])
    inc = 0
    bar = ProgressBar(len(c.video_urls)*2,prefix="Downloading",suffix="Preparing",bar_length=YSIZE,spinner_type="s")
    for video in c.video_urls:
        bar.iter()
        try:
            y = pytube.YouTube(video)
            bar.suffix = y.title
            bar.iter()
            st = y.streams.get_highest_resolution()
            st.download(filename=f"vid_{inc}.mp4")
        except:
            bar.iter()
            try:
                os.remove(f"vid_{inc}.mp4")#Removing corrupt video if applicable
            except:
                pass
            continue
        inc += 1
    bar.wait()
    bar.stop()
    if not _exv:
        sys.exit() #No point in throwing filenotfound error
if _exv:
    g = glob.glob("*.mp4")
    bar = ProgressBar(int(len(g)*2),prefix="Extracting",suffix="Preparing",bar_length=YSIZE,spinner_type="s")
    for v in g:
        bar.iter()
        _len = int(get_length(v) // 1)# Rounding down
        if _len > 2:
            slt = random.randint(0,_len)
            bar.suffix = str(v)
            rmn = subprocess.run(["ffmpeg","-ss",str(slt),"-i",os.getcwd()+sfs+v,"-t","1",os.getcwd()+sfs+v.split(".")[0]+"s.mp4"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            bar.iter()
            rmn2 = subprocess.run(["ffmpeg","-i",os.getcwd()+sfs+v.split(".")[0]+"s.mp4","-filter_complex","[0:v]pad=1280:720:-1:-1,fps=30000/1001[v];[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a]","-map","[a]","-map","[v]",os.getcwd()+sfs+v.split(".")[0]+"x.mp4"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        else:
            bar.iter()

    bar.wait()
    bar.stop()
print("Verifying Files")
#Removing empty files to prevent glitvhes
fls = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(),f))]
for file in fls:
    if os.path.getsize(file) == 0:
        try:
            os.remove(file)
        except:
            print("Failed to remove corrupt file")
print("Creating list")
lg = glob.glob("*x.mp4")#Filtering split videos only
data = ""
for vid in lg:
    data += "file '"
    data += os.getcwd()
    data += sfs
    data += vid
    data += "'\n"
with open("mylist.txt","w+") as f:
    f.write(data)
print("Compiling...")
rmn2 = subprocess.run(["ffmpeg","-f","concat","-safe","0","-i","mylist.txt","output.mp4"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if "--nowaste" in args:
    print("Cleaning...")
    if not os.path.isdir(".output"):
        os.mkdir(".output")
    shutil.copyfile("output.mp4",os.getcwd()+f"{sfs}.output{sfs}output.mp4")
    [os.remove(fl) for fl in glob.glob("*.mp4")]#LOL List comprehensions go BRR (excuse my use of 21st century humor)
    try:
        os.remove("mylist.txt")
    except:
        pass
    shutil.copyfile(os.getcwd()+f"{sfs}.output{sfs}output.mp4","output.mp4")
    shutil.rmtree(".output")
    try:
        os.rmdir(".output")
    except:
        pass
print("Done!")
