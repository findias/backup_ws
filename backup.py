import os
import time
import logging
import shutil

__author__ = 'Konstantin Kovalev'

# -*- coding: utf-8 -*-

start_time = time.time()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

user_name = 'konkov'
home_dir = "/home/" + user_name
backup_folder = home_dir + '/Documents/scripts/backup_folder'
arch_name = 'backup_' + time.strftime("%d_%m_%Y_%H-%M")
arch_path = '/opt/backup/'
arch_file_path = arch_path + arch_name
configs_file = home_dir + '/.config'
configs_file_for_backup = {
    'ssh':      [home_dir + '/.ssh/', []],
    'nvim':     [configs_file + '/nvim/', ['init.vim', 'coc-settings.json']],
    'i3':       [configs_file + '/i3/', []],
    'neofetch': [configs_file + '/neofetch/', []],
    'nitrogen': [configs_file + '/nitrogen/', []],
    'picom':    [configs_file + '/picom/', ['picom.conf']],
    'rofi':     [configs_file + '/rofi/', ['config.rasi']],
}

''' Copy backup files in destenation folder'''

def create_backup(backup_files, dst_path):
    logging.info('----=== Start copy files ===----')
    for key, value in backup_files.items():
        gen_path = dst_path + value[0]
        ''' Check: if folder is not exist create folder '''
        if not os.path.exists(gen_path):
            os.makedirs(gen_path)
        # Backup only selected file
        if value[1] != list():
            for i in value[1]:
                src_copy_path = os.path.join(value[0], i)
                shutil.copy(src_copy_path, gen_path)
                logging.info("Config " + key + " is copy in " + gen_path + i)
        # Backup folder with all files
        else:
            for file in os.listdir(value[0]):
                src_copy_path = os.path.join(value[0], file)
                shutil.copy(src_copy_path, gen_path)
                logging.info("Config " + key + " is copy in " + gen_path + file)

''' Get last archive'''

def find_last_file(dir):
    logging.info("----==== Start find and get last backup archive ====----")
    f_list = os.listdir(dir)
    if f_list:
        f_list = [os.path.join(dir, file) for file in f_list]
        f_list = [file for file in f_list if os.path.isfile(file)]
        last_file = max(f_list, key=os.path.getctime)
        logging.info("----====" + last_file + " is last achive ====----")
        return last_file
    else:
        logging.warning("----==== Current folder " + f_list + " is empty ====----")

def archive_backup():
    logging.info('----==== Create archive ====-----')
    shutil.make_archive(arch_file_path, 'gztar', backup_folder)


if __name__ == '__main__':
    if (os.name == 'posix') and (user_name == os.getlogin()):  # Check OS and username
        try:
            find_last_file(arch_path)
            create_backup(configs_file_for_backup, backup_folder)
            archive_backup()
        except Exception as e:
            logging.exception(e)
        else:
            print('Backup is success')
    else:
        print('Backup did not pass checking')
    print("--- %s seconds ---" % (time.time() - start_time))
