import os
import sys
import platform
import Window
import Parser


fileName = ""
file = ""
outFile = ""

createOutDir = False
isWindows = False


def showOption():
    print("   --help    | -h  --> Show this message")
    print("   --output  | -o  --> Store output file in output folder")


def showHelp():
    print("\n      UE Capability Information Parser v0.2")
    print("Written by Breno T. Minzon - breno.minzon@gmail.com")
    print("Usage:")
    print("       UECapabilityInformation <option> <filename>")
    print("       if <filename> is omitted, program main window will appear, allowing to paste/load file")
    print("Options:")
    showOption()
    quit()


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        i = 1
        for i in range(1, len(sys.argv)-2):
            option = sys.argv[i]
            if option.startswith("-"):
                if option.find("--output") != -1 or option.find("-o") != -1:
                    createOutDir = True
                    break
                else:
                    print("Invalid argument. Current supported options are:")
                    showOption()
                    quit()
        fileName = sys.argv[i+2]
#            else:
#                print("Invalid argument. Current supported options are:")
#                showOption()
#                quit()
    elif len(sys.argv) == 2:
        if sys.argv[1].find("--help") != -1 or sys.argv[1].find("-h") != -1:
            showHelp()
            quit()
        else:
            fileName = sys.argv[1]
    else:
        Window.showUI()
        quit()

    if fileName == "":
        print("Must provide a file while running in command mode. Please try again")
        quit()

    # creates output file with the same name as input
    outFile = fileName.replace(".txt", ".xlsx")
    # determine which OS script is running
    if platform.system() == "Windows":
        isWindows = True
    # If the file already exists, don't need to run again, but only uses the result
    if isWindows and os.path.isfile("output\\"+outFile):
        print("File exists. No need to run")
        print("End program")
        quit()
    # Open file as read only
    file = open(fileName, 'r')
    lines = file.readlines()
    file.close()

    # main program
    Parser.readInformation(lines, outFile)

    # If option --output was passed, it will store the output file in the output directory
    if createOutDir:
        if platform.system() == "Windows":
            if not os.path.isdir("output\\"):
                os.system("mkdir output")
            os.system("mv " + outFile + " output")
    print("End program")
