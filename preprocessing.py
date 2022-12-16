import os
import argparse
import sys
import string

    
def main(inputpath, outputpath):
    if os.path.isfile(inputpath):
        f = open(inputpath, 'r+')
        file_contents = f.read()
        f.close()
    else:
        raise FileNotFoundError(f'File {inputpath} is not found. Retry with another name')
    new_contents = file_contents.replace('<t>', '<triple>').replace(('<sj>'), ' ').replace('<p>', ' | ').replace('<o>',' | ').replace('\n', ' <triple>   random\n')
    #Outputting adjusted file
    outFile = open(outputpath, 'w')
    outFile.write(new_contents)
    outFile.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adjusting Hypo")
    parser.add_argument("--input", type=str, default='comparison_test_data/hypo',
                        help="Please provide the pathname to the hypothesis file that needs to be adjusted to GAN test_data.txt format")
    
    parser.add_argument("--output", type=str, default='comparison_test_data/hypo-GAN-pt',
                        help="Please provide an output path for the formated hypothesis file")
    
    args = parser.parse_args()
    main(args.input, args.output)        