clean_out_words=['+2','iI','+ ', '+\n', '   2', '+!', '+(','+*', '+<',]
def clean_text(byte_string):
    '''
    Given the byte_string in the 'attributedBody' column, this code tries to extract the text in the message.
    '''
    if byte_string is None:
        return None
    s = extract_substring(extract_ascii_text(byte_string))
    for word in clean_out_words:
        s = s.replace(word,'')
        
    return s

            
def convert_handle_id_to_contact_info(handle_id, handles):
    ''' 
    Given a handle_id, this will give you the contact_info.
    It is confirmed that each handle_id has a unique contact info. 
    '''
    _ = handles.loc[handles['handle_id']==handle_id]
    if handle_id==0:
        #this is expected
        return None
    if len(_)!=1 and handle_id!=0:
        #for handle_ids that are not 0, this should not happen
        print(f'Multiple rows for {handle_id}')
        return None
    else:
        return handles.loc[handles['handle_id']==handle_id]['contact_info'].iloc[0]

    
def update_contact_info(contact_info, contact_info_list, message_id):
    '''
    This is needed because many sent messages don't have the contact that the messages was sent to.
    If the chat is a 1-1 chat then the message was sent to the only other participant in the chat.
    If the caht is a group-chat, I currently just assign it a 'group-chat' contact info, since there is no signle recipient of the message. 
    '''
    if contact_info_list is None:
        return 'contact list is none'
    if len(contact_info_list)==1:
        if contact_info is None:
            return contact_info_list[0]
        else: 
            # contact info is not None
            if contact_info!=contact_info_list[0]:
                # while this could happen with handles, this should not happen with contact info because two different handles for the same contact info have the same ... contact info.
                print(contact_info, contact_info[0], message_id)
            else:
                #if the handle_id is not zero, it should match the handle_id in the chat and in that case we just keep it as is.
                return contact_info
    else:
        # this is a group chat
        # i could explore having chat_id here but i don't have that info right now.
        return 'group-chat'
    

def get_handle_and_contact_list(chat_id,chat_handle_join, handles):
    '''
    Takes in the id of the chat, chat_id, and returns two lists. One list with all the handle_ids of the participants in that chat.
    And one contact_list with the contact information (phone number or email) in the chat. 
    chat_handle_join is the dataset that translates the chat_id to handle_id
    and handles is the dataset that translates the handle_id to the contact info.
    '''
    if chat_id is not None:
        handle_list = list(chat_handle_join.loc[chat_handle_join['chat_id']==chat_id]['handle_id'].unique())
        contact_list = []
        for handle_id in handle_list:
            contact_list.append(convert_handle_id_to_contact_info(handle_id, handles))
        return handle_list, contact_list
    else:
        return None
                    

def get_chat_size(handles_list):
    '''
    Given the list of handles in a chat thread, returns the size of the list, i.e., the number of unique handles in the chat. 
    '''
    if handles_list is None:
        return 0
    else:
        return len(handles_list)
    

def get_rolling_avg(daily_count, column_name='received_messages', window_size=7):
    ''' Take a df as an input and returs the rolling average of the column name'''
    daily_count_df = daily_count.reset_index(name=column_name)
    daily_count_df = daily_count_df.sort_values('date')
    daily_count_df.set_index('date', inplace=True)

    daily_count_df['running_avg'] = daily_count_df[column_name].rolling(window=window_size).mean()
    return daily_count_df


# Other functions that are not currently being used.
def get_handles_in_the_chat(message_id, chat_message_joins, chat_handle_join ):
    '''
    Given a message_id this will give you a list of all the handle_id that are in
    the chat that the message_id was sent
    '''
    chats = chat_message_joins.loc[chat_message_joins['message_id']==message_id]
    if len(chats)==1:
        chat_id = chats['chat_id'].iloc[0]
        handles_in_chat = chat_handle_join.loc[chat_handle_join['chat_id']==chat_id]
        return list(handles_in_chat['handle_id'].unique())
    else:
        return None
        
def get_chat_type(message_id, chat_message_joins, chat_handle_join):
    # print(message_id)
    chats = chat_message_joins.loc[chat_message_joins['message_id']==message_id]
    if len(chats)==0:
        return 'no-chat-id'
    elif len(chats)>1:
        return 'mutlitple-chats'
    else:
        chat_id = chats['chat_id'].iloc[0]
        handles_in_chat = chat_handle_join.loc[chat_handle_join['chat_id']==chat_id]
        if len(handles_in_chat)>1:
            return 'group-chat'
        elif len(handles_in_chat)==0:
            return 'empty'
        else:
            return 'one-on-one'


def extract_ascii_text(byte_string):
    extracted_text = ""

    for byte in byte_string:
        char = chr(byte)
        if char.isprintable() or char in ['\n', '\t', ' ']:
            extracted_text += char
        else:
            extracted_text += " "

    return extracted_text

def extract_substring(s, x1='NSString', x2='NSDictionary'):
    # Find the start index of x1 and the end index of x2
    start_index = s.find(x1)
    end_index = s.find(x2)

    # Check if both substrings are found
    if start_index != -1 and end_index != -1:
        # Adjust indices to include x1 and exclude x2
        start_index += len(x1)
        
        # Extract and return the substring
        return s[start_index:end_index].strip()
    else:
        # Return an empty string or a specific message if not found
        return "Substrings not found or in incorrect order"
    
def get_contact_info_in_the_chat(message_id, chat_message_joins,chat_handle_join, handles):
    '''
    Given a message_id, uses the convert_handle_id_to_contact_info to convert the handle_ids into contact_info list
    '''
    chats = chat_message_joins.loc[chat_message_joins['message_id']==message_id]
    if len(chats)==1:
        chat_id = chats['chat_id'].iloc[0]
        handles_in_chat = chat_handle_join.loc[chat_handle_join['chat_id']==chat_id]
        contact_list = []
        for handle_id in handles_in_chat['handle_id'].unique():
            # make sure the handle_id has only 
            contact_list.append(convert_handle_id_to_contact_info(handle_id, handles))
        return contact_list
    else:
        # print(len(chats), message_id)
        return None
