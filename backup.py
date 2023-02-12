import os
import tarfile
import time
import logging
import shutil
import hashlib
import gnupg


__author__ = 'Konstantin Kovalev'

# -*- coding: utf-8 -*-

start_time = time.time()

logging.basicConfig(
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    datefmt='%d-%b-%y %H:%M:%S',
                    filename='/opt/backup/backup.log',
                    filemode='a'
                    )
# Params for path source
user_name = os.getlogin()
home_dir = os.path.join('/home/', user_name)
doc_dir = os.path.join(home_dir, 'Documents')
configs_file = home_dir + '/.config'

# Params for destenation backup folder
backup_folder = 'backup'
backup_folder_path = os.path.join(doc_dir, backup_folder)

# Params for archive
arc_file_name = 'backup_' + time.strftime("%d_%m_%y_%H-%M") + '.tar.gz'
path_for_arc = '/opt/backup/'
arc_file_path = path_for_arc + arc_file_name
curr_file_path = path_for_arc + 'curr_backup.tar.gz'

# Params for encrypt
encrypt = True
id_key = 'findias@bk.ru'
encrypt_dir = os.path.join(home_dir, '.gnupg')

# Config for backup data
configs_file_for_backup = {
    'ssh':      [os.path.join(home_dir, '.ssh/'), []],
    'nvim':     [os.path.join(configs_file, 'nvim/'), ['init.vim', 'coc-settings.json']],
    'i3':       [os.path.join(configs_file, 'i3/'), []],
    'neofetch': [os.path.join(configs_file, 'neofetch/'), []],
    'nitrogen': [os.path.join(configs_file, 'nitrogen/'), []],
    'picom':    [os.path.join(configs_file, 'picom/'), ['picom.conf']],
    'rofi':     [os.path.join(configs_file, 'rofi/'), ['config.rasi']],
    'root':     [home_dir, ['.zshrc', '.zshrc.pre-oh-my-zsh', '.zsh_history', 'first_sc.sh']],
    # 'my_data':  [os.path.join(doc_dir, 'bd_pass/'), []],
    'stocks':   [os.path.join(doc_dir,  'stocks/'), []],
    'db_pg':    [os.path.join(doc_dir, 'bd_postgress/'), []],
    'alacritty':[os.path.join(configs_file, 'alacritty/'), []],
    # 'oh-my-zsh':    [os.path.join(home_dir, '.oh-my-zsh/'), []],
}

''' Copy backup files in destenation folder'''


def create_backup(backup_files, dst_path):
    logging.info('----=== Start copy files ===----')
    list_file_for_backup = []
    # Clear and create backup folder
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    else:
        shutil.rmtree(dst_path)
        os.makedirs(dst_path)
    # Take a config dictionary and copy in backup folder
    for key, value in backup_files.items():
        gen_path = dst_path + value[0]
        ''' Check: if folder is not exist create folder '''
        if not os.path.exists(gen_path):
            os.makedirs(gen_path)
        # Backup only selected file
        if len(value[1]) != 0:
            for i in value[1]:
                src_copy_path = os.path.join(value[0], i)
                shutil.copy2(src_copy_path, gen_path)
                path_file = os.path.join(gen_path, i)
                list_file_for_backup.append(path_file)
                logging.info("Config " + key + " is copy in " + path_file)
        else:
            shutil.copytree(value[0], gen_path, dirs_exist_ok=True)
            path_file = os.path.join(gen_path, value[0])
            list_file_for_backup.append(path_file)
            logging.info("Config " + key + " is copy in " + path_file)
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
        md5_sum = md5_hash.hexdigest()
        logging.info('----==== Check sum for file ' + filename + ' is ' + md5_sum + ' ====----')
        return md5_sum


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
            logging.info('----==== Check archive is complete ====----')
    except Exception as e:
        logging.warning('Check is failing. ' + file + 'is a bad archive')
        logging.exception(e)


def gpg_encrypt(gpg_dir, data, recipients, do_enc):
    if do_enc:
        logging.info('----==== Start encryption archive ====----')
        encrypt_file_name = data + '.crypt'
        gpg = gnupg.GPG(gnupghome=gpg_dir)
        crt_encrypt_file = gpg.encrypt_file(data, recipients, output=encrypt_file_name)
        logging.info('----==== Success encryption archive ' + encrypt_file_name + ' ====----')
        return crt_encrypt_file


if __name__ == '__main__':
    if (os.name == 'posix') and (user_name == os.getlogin()):  # Check OS and username
        try:
            # find_last_file(path_for_arc)
            create_backup(configs_file_for_backup, backup_folder_path)
            archive_backup(arc_file_path, backup_folder_path, './backup')
            archive_backup(curr_file_path, backup_folder_path, './backup')
            check_archive(arc_file_path)
            check_archive(curr_file_path)
            check_archive(arc_file_path)
            gpg_encrypt(encrypt_dir, arc_file_path, id_key, encrypt)
            gpg_encrypt(encrypt_dir, curr_file_path, id_key, encrypt)
            get_hash(arc_file_path)
        except Exception as e:
            logging.exception(e)
        else:
            logging.info('----==== Buckup is complete ====----')
    else:
        print('Backup did not pass checking')
print("--- %s seconds ---" % (time.time() - start_time))