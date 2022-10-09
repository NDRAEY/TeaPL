import shutil

def clean():
    shutil.rmtree("tea_pl.egg-info", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)

if __name__=="__main__":
    clean()
