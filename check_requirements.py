import os
import subprocess
import sys
import pkg_resources

def check_requirements(requirements_file):
    # Get the absolute path of the requirements file
    requirements_file_path = os.path.join(os.path.dirname(__file__), requirements_file)
    
    with open(requirements_file_path, 'r') as file:
        libraries = file.readlines()
    
    missing_libraries = []
    
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    for library in libraries:
        library = library.strip()
        if library:
            if library not in installed_packages:
                missing_libraries.append(library)
    
    if missing_libraries:
        print("The following libraries are missing and will be installed:")
        for lib in missing_libraries:
            print(f"- {lib}")
            try:
                # Attempt to install the missing library
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"Successfully installed {lib}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {lib}")
    else:
        print("All libraries are available.")

if __name__ == "__main__":
    check_requirements('requirements.txt')