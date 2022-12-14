import csv
from utility import (wideNumInStr, print_spliter, clear_screen)
from settings import (SLEEP_TIME)
import os
import copy
import time

def prepare_item_list():
    '''
        Load data from ./data/.

        return:
            item_list: Dict that key is type of device, value is List of device of that type.
                       Each item in List is a Dict that the same structure with ./data/ CSV file.
            _sum: Total number of devices in item_list. Save this because of divided by type,
                  we cannot easily access that length of item_list by len().
    '''
    global item_index
    def load_data(file, item_list):
        '''
            Load data by filename, and add into item_list.
        '''
        global item_index   # cannot use item_index within with scope
        with open(file, newline='', encoding='utf-8') as csvfile:
            rows = csv.DictReader(csvfile)
            _type = file.split(' ')[-1][:-4]    # get the file name as item type
            item_list[_type] = []
            for row in rows:
                row['項次'] = item_index    # give every item an unique number
                row['數量'] = int(row['數量'])
                row['未稅單價'] = int(row['未稅單價'])
                # row['分類'] = _type
                item_list[_type].append(row)
                item_index += 1

    def parse_filename(data_dir):
        '''
            Load filename from data_dir, and sort by the prefix number in filename.
        '''
        filenames = os.listdir(data_dir)
        filenames = [i for i in filenames if i.endswith('csv')] # for Mac
        filenames.sort(key=lambda x: int(x.split()[0]))
        return filenames

    item_list = {}
    item_index = 1
    data_dir = './data/'
    filenames = parse_filename(data_dir)
    for filename in filenames:
        load_data(data_dir + filename, item_list)
    _sum = 0
    for item in item_list.values():
        _sum += len(item)   # calculate the total number of item
    return item_list, _sum

def print_item_list():
    '''
        Print all items in ./data/.
    '''
    print(f' 項次 | {"器材內容":^{71}}| 數量 | 器材編號 | 未稅單價')
    for _type, items in item_list.items():
        print_spliter(f'{_type:^{30 - len(_type)}}', 40)
        for item in items:
            context_ch_width = wideNumInStr(item["器材內容"])   # calculate the number of full width word
            print(f'{item["項次"]:4d}  | {item["器材內容"]:{75 - context_ch_width}}|{item["數量"]:>5d} |          |{item["未稅單價"]:>9d}')
    print()

def show_item_list(clear=True):
    '''
        Command '1', print all items that was selected.
    '''
    if clear:
        clear_screen()
        print('【目前已加入之品項清單】\n')
    export_item_list.sort(key=lambda x: x['項次'])  # sort by unique number of item
    print(f' 項次 | {"器材內容":^{71}}| 數量 | 器材編號 | 未稅單價')
    for item in export_item_list:
        context_ch_width = wideNumInStr(item["器材內容"])
        print(f'{item["項次"]:4d}  | {item["器材內容"]:{75 - context_ch_width}}|{item["數量"]:>5d} |          |{item["未稅單價"]:>9d}')
    print()

def add_item():
    '''
        Command '2', add items into selected item list.
        Enter q to stop adding.
    '''
    def find_and_insert_item(command):
        '''
            Find item with command and insert into selected item list.
        '''
        for items in item_list.values():    # iterate through all type of item
            if command <= len(items):   # find the item
                item = items[command - 1]
                while 1:
                    nums = input('請輸入數量(輸入q以取消加入品項)：')
                    if nums == 'q': # Leave
                        print('\n已取消加入品項')
                        return
                    try:
                        nums = int(nums)
                        if nums > 0 and nums <= item['數量']:   # Success
                            new_item = copy.copy(item)
                            new_item['數量'] = nums
                            export_item_list.append(new_item)
                            export_item_index_set.add(new_item['項次'])
                            print(f'成功加入品項：{new_item["項次"]} {new_item["器材內容"]} {new_item["數量"]}個')
                            return
                        elif nums == 0: # Error
                            print('【警告】輸入數量不可為0，請重新輸入！')
                        else:   # Error
                            print('【警告】輸入數量大於庫存數量，請重新輸入！')
                    except: # Error
                        print('【警告】只接受整數輸入，請重新輸入！')
            command -= len(items)
    while 1:
        clear_screen()
        print('【加入新品項】\n')
        print_item_list()
        command = input('輸入項次編號以加入新品項(輸入q以停止加入品項)：')
        if command == 'q':  # Leave
            clear_screen()
            break
        try:
            command = int(command)
            if command >= 1 and command <= item_list_sum and command not in export_item_index_set:  # Success
                find_and_insert_item(command)
            elif command < 1 or command > item_list_sum:    # Error
                print('【警告】項次編號超出範圍，請重新輸入！')
            elif command in export_item_index_set:  # Error
                print('【警告】該品項已存在，請重新輸入或刪除原先品項！')
            time.sleep(SLEEP_TIME)
        except: # Error
            print('【警告】只接受整數輸入，請重新輸入！')
            time.sleep(SLEEP_TIME)


def delete_item():
    '''
        Command '3, delete items from selected item list.
    '''
    while 1:
        clear_screen()
        print('【刪除品項】\n')
        show_item_list(clear=False)
        command = input('請輸入欲刪除之品項編號(輸入q以停止刪除)：')
        if command == 'q': # Leave
            clear_screen()
            break
        try:
            command = int(command)
            f = False
            for idx, item in enumerate(export_item_list):
                if item['項次'] == command: # Success
                    del export_item_list[idx]
                    export_item_index_set.remove(item['項次'])
                    f = True
                    break
            if not f:   # Error
                print('【警告】輸入品項編號不存在，請重新輸入！')
                time.sleep(SLEEP_TIME)
        except: # Error
            print('【警告】只接受整數輸入，請重新輸入！')
            time.sleep(SLEEP_TIME)

def export_to_csv():
    clear_screen()
    print('【輸出CSV檔案】\n')
    print('請確認目前器材清單：\n')
    show_item_list(clear=False)
    filename = input('請輸入輸出檔案名稱(不需輸入副檔名)：')
    if not os.path.exists('./export/'):
        os.mkdir('./export/')
    with open('./export/' + filename + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['項次', '器材內容', '數量', '器材編號', '未稅單價'])
        for item in export_item_list:
            writer.writerow(item.values())
    print(f'已輸出檔案至./export/{filename}.csv，可繼續以目前器材清單繼續操作，或是以指令5清空器材清單以建立新的清單，或是以指令6結束程式\n')

item_list, item_list_sum = prepare_item_list()
command_list = {
    '1' : show_item_list,
    '2' : add_item,
    '3' : delete_item,
    '4' : export_to_csv,
}
f = True
while f:
    export_item_list = []
    export_item_index_set = set()
    while 1:
        command = input('指令清單：\n'
            '1  顯示目前器材清單\n'
            '2  加入品項至器材清單\n'
            '3  自器材清單刪除品項\n'
            '4  輸出CSV檔案\n'
            '5  清空器材清單\n'
            '6  結束程式\n'
            '請輸入指令：')
        if command == '5':
            clear_screen()
            print('已清除器材清單！\n')
            break
        elif command == '6':
            f = False
            break
        try:
            command_list[command]()
        except KeyError:    # Error
            print('【警告】指令錯誤，請重新輸入！')
            time.sleep(SLEEP_TIME)
            clear_screen()
print('執行完成，結束程式')
