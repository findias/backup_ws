import os
import tarfile
import time
import logging
import shutil
import hashlib

__author__ = 'Konstantin Kovalev'

# -*- coding: utf-8 -*-

start_time = time.time()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

user_name = 'konkov'
home_dir = os.path.join('/home/', user_name)
backup_folder = 'backup_folder'
backup_folder_path = home_dir + '/Documents/scripts/' + backup_folder
arc_file_name = 'backup_' + time.strftime("%d_%m_%Y_%H-%M") + '.tar.gz'
path_for_arc = '/opt/backup/'
arc_file_path = path_for_arc + arc_file_name
configs_file = home_dir + '/.config'
configs_file_for_backup = {
    'ssh':      [home_dir + '/.ssh/', []],
    'nvim':     [configs_file + '/nvim/', ['init.vim', 'coc-settings.json']],
    'i3':       [configs_file + '/i3/', []],
    'neofetch': [configs_file + '/neofetch/', []],
    'nitrogen': [configs_file + '/nitrogen/', []],
    'picom':    [configs_file + '/picom/', ['picom.conf']],
    'rofi':     [configs_file + '/rofi/', ['config.rasi']],
    'zshrc':    [home_dir, ['.zshrc', '.zshrc.pre-oh-my-zsh', '.zsh_history', 'first_sc.sh']],
}

''' Copy backup files in destenation folder'''


def create_backup(backup_files, dst_path):
    logging.info('----=== Start copy files ===----')
    list_file_for_backup = []
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
                list_file_for_backup.append(gen_path + i)
                logging.info("Config " + key + " is copy in " + gen_path + i)
        # Backup folder with all files
        else:
            for file in os.listdir(value[0]):
                src_copy_path = os.path.join(value[0], file)
                shutil.copy(src_copy_path, gen_path)
                list_file_for_backup.append(gen_path + file)
                logging.info("Config " + key + " is copy in " + gen_path + file)
    logging.info('----==== Copy files is complete ====----')
    return list_file_for_backup


''' Get last archive. Return name last of file'''


def find_last_file(dir):
    logging.info("----==== Start find and get last backup archive ====----")
    f_list = os.listdir(dir)
    if f_list:
        f_list = [os.path.join(dir, file) for file in f_list]
        f_list = [file for file in f_list if os.path.isfile(file)]
        last_file = max(f_list, key=os.path.getctime)
        logging.info("----==== " + last_file + " is last achive ====----")
        return last_file
    else:
        logging.warning('----==== Current folder ' + dir + ' is empty ====----')


''' Create hash sum and return md5_sum'''


def get_hash(filename):
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
     # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        md5_summ = md5_hash.hexdigest()
        logging.info('----==== Check sum for file ' + filename + ' is ' + md5_summ + ' ====----')
        return md5_summ


def archive_backup(create_arc_file, src_folder, arcname):
    logging.info('----==== Start create archive ====-----')
    with tarfile.open(create_arc_file, 'w:gz') as tar:
        tar.add(src_folder, arcname)
    logging.info('----==== Create archive is success. Name file is ' + create_arc_file + ' ====----')


''' Check archive '''


def check_archive(file):
    try:
        logging.info('----==== Check archive is starting ====----')
        check_list = []
        with tarfile.open(file) as tar:
            for name in tar.getmembers():
                check_list.append(name)
            logging.info('----==== Check archive is complete ====----')   # TODO Add out in file.
    except Exception as e:
        logging.warning('Check is failing. ' + file + 'is a bad archive')
        logging.exception(e)


if __name__ == '__main__':
    if (os.name == 'posix') and (user_name == os.getlogin()):  # Check OS and username
        try:
            # find_last_file(path_for_arc)
            create_backup(configs_file_for_backup, backup_folder_path)
            archive_backup(arc_file_path, backup_folder_path, './backup_folder')
            check_archive(arc_file_path)
             # print(get_hash(find_last_file(arch_path)))
            # tar =tarfile.open('/opt/backup/tbackup.tar.gz', 'r:gz')
            # print(tar.gettarinfo())
            # tar.close()
        except Exception as e:
            logging.exception(e)
        else:
            logging.info('----==== Buckup is complete ====----')
    else:
        print('Backup did not pass checking')
print("--- %s seconds ---" % (time.time() - start_time))
