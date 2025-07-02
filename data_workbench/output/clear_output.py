import os
import shutil

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def clear_output():
    for root, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
        for name in files:
            if name == '.gitkeep' or name == os.path.basename(__file__):
                continue
            file_path = os.path.join(root, name)
            os.remove(file_path)
        for name in dirs:
            dir_path = os.path.join(root, name)
            if os.path.exists(os.path.join(dir_path, '.gitkeep')) and len(os.listdir(dir_path)) == 1:
                continue
            shutil.rmtree(dir_path, ignore_errors=True)
    print(f'Папка {OUTPUT_DIR} очищена.')

if __name__ == '__main__':
    clear_output() 