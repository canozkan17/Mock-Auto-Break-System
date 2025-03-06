from DES_constants import * 
import math
import datetime
import sqlite3
import os.path

 


class DES_Encryption_Decryption:

    
    def Encrypt_to_db(self,vehicle_object:object, master_key):

        object_creation_time = vehicle_object.date_time.strftime("%f") # NANO SECONDS OF THE TIME OF THE PASSED VEHICLE OBJECT CREATION
        seed = vehicle_object.speed_kmh

        key = self.DES_key_generation(seed,object_creation_time) # GENERATES KEY - phase 1

        self.Encrypt_keys(key,master_key)
       
        binary_key = self.DES_key_conversion_to_binary(key) # TURNS THE KEY TO BINARY

        generated_sub_keys = self.DES_sub_key_generation(binary_key) # GENERATES SUBKEYS

        dict_keys = list(vehicle_object.collected_data)

        for i in range(len(dict_keys)):
            value = vehicle_object.collected_data[f"{dict_keys[i]}"] # GETS EACH VALUE IN THE COLLECTED DATA INDIVIDUALLY
            
            # GETTING BINARY VERSION OF THE VALUE
            binary_val = ""
            byte_array = bytearray(str(value),'utf-8')

            for j in byte_array:
                binary_val_add = bin(j)[2:].zfill(8)
                binary_val += binary_val_add 
            
            processed_value = self.DES_Operations(binary_val,generated_sub_keys) # STARTS ENCRYPTING 
            required_bytes = (len(processed_value) + 7) // 8
            hex_lenght = required_bytes * 2 
            processed_value = hex(int(processed_value,2))[2:].zfill(hex_lenght) # RETURNING ENCRYPTED VALUE AS HEX STRING

            vehicle_object.collected_data.update({f"{dict_keys[i]}": processed_value})


    def Decrypt_from_db(self,database_obejct:object,master_key):
        db = database_obejct

        db.create_Decrypted_db()

        connection = sqlite3.connect("Loggs.db")
        cursor = connection.cursor()

        cursor.execute("SELECT row_id FROM decrypted_data ORDER BY row_id DESC")

        try:
            last_line = cursor.fetchone()[0]
            last_line += 1
        except:
            last_line = 1

        lines , keys = self.Decrypt_keys(master_key)

        cursor.execute("PRAGMA table_info(logged_data)")

        row_names = cursor.fetchall() # GETTING THE ROW NAMES AS LIST FORM 
        dict_data = {}

        for line in range(lines):
            cursor.execute(f"SELECT * FROM logged_data WHERE row_id ='{last_line}' ORDER BY row_id")
            encyrpted_line = cursor.fetchall()[0] # GETS THE LINE OF THE ENCRYPTED DATA

            # KEY OPERATIONS
            binary_key = self.DES_key_conversion_to_binary(keys[line]) # TURNS THE KEY TO BINARY
            generated_sub_keys = self.DES_sub_key_generation(binary_key) # GENERATES SUBKEYS         
            generated_sub_keys.reverse() # REVERSING THE ORDER FOR DECRYPTION   

            for item in range(len(encyrpted_line)):
                dict_data.update({f"{row_names[item][1]}": encyrpted_line[item]})
                if item == 0:
                    continue
                else:
                    value = encyrpted_line[item]
                    # TURNS THE THE VALUE INTO BINARY FOR PROCESSING 
                    binary_length = len(value) * 4
                    binary_val = bin(int(value, 16))[2:].zfill(binary_length)

                    processed_value = self.DES_Operations(binary_val,generated_sub_keys)

                    # Split the binary string into 8-bit chunks (bytes)
                    byte_list = [processed_value[b:b+8] for b in range(0, len(processed_value), 8)]
                    
                    # Convert each 8-bit chunk to an integer, then create a bytes object
                    byte_array = bytes([int(bv, 2) for bv in byte_list])
                    
                    # Decode the bytes object using UTF-8
                    processed_value = byte_array.decode('utf-8')
                    
                    # Get the padding size from the last byte (interpreted as a character)
                    padding_size = ord(processed_value[-1])
                    # Remove the padding and return the plain text
                    processed_value = processed_value[:(-padding_size)]
                    dict_data.update({f"{row_names[item][1]}": processed_value})
            last_line += 1
            db.insert_to_Decrypted_db(dict_data)
            
    # GENERATES 8 ASCII CHAR STRING KEY - TOTAL 64 BITS
        # VEHICLE SPEED IS USED FOR SEED 
        # GENERATES 8 RANDOM INTEGERS
            # USING SEED, VEHICLE OBJECT CREATION TIME NANO SECONDS, AND ENCYPTION TIME START NANO SECONDS
        # ACCORDING TO THE PROPERTY OF THE GENERATED INTIGERS SELECTS A LETTER OR NUMBER FOR ALPHA-NUMERICAL KEY 
    def DES_key_generation(self,seed,object_creation_time):
        
        temp = 0
        key = ""
        seed = seed
        # ENG ALPHABET IS USED FOR 64 BIT INITIAL KEY 
        upper_eng_alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        lower_eng_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        num_list =           ['1', '2', '3', '4', '5', '6', '7', '8', '9']


        #PREPPING CONSTANTS THROUGH TIME STAMPS
        key_creator_const_c = int(object_creation_time)
        key_creator_const_a = int(datetime.datetime.now().strftime("%f")) # NANO SECONDS OF THE ENCRYPTION START TIME
        mode_letter_count_m = len(upper_eng_alphabet)


        # A - 1 SHOULD BE DIVISIBLE BY M
        if (key_creator_const_a - 1) % mode_letter_count_m != 0:
            key_creator_const_a -= (key_creator_const_a - 1) % mode_letter_count_m

        # GCD(M,C) = 1 
        if math.gcd(mode_letter_count_m,key_creator_const_c) != 1:
            while math.gcd(mode_letter_count_m,key_creator_const_c) != 1:
                key_creator_const_c += 1

        # IF STATEMENT FOR RANDOM ALPHA-NUMERITICAL KEY GENERATION
            # RUNS THE (SEED * B) + A MOD C FORMULA

            # MULTIPLE OF 5 == NUMBER
            # EVEN NUMBER == CAPITAL LETER
            # ODD NUMBER == LOWER LETTER
                # WRITES INTO KEY IN WHICHEVER CHAR SET THE TEMP IS 

            # RE-SETS THE SEED
        for i in range(8):
            temp = (((seed * key_creator_const_a) + key_creator_const_c) % mode_letter_count_m) 
            if temp % 5 == 0:
                key += num_list[temp % len(num_list)]
            elif temp % 2 == 0:
                key += upper_eng_alphabet[temp % 26]
            else:
                key += lower_eng_alphabet[temp % 26]
            seed = ((seed * key_creator_const_a) + key_creator_const_c) % mode_letter_count_m
        
        return key
    
    # TURNS THE THE KEY INTO BINARY FOR PROCESSING 
    def DES_key_conversion_to_binary(self,key):
        
        binary_key = ""
        byte_array = bytearray(key,'utf-8')

        for i in byte_array:
            binary_val = bin(i)[2:].zfill(8)
            binary_key += binary_val 
    
        return binary_key

    # GENERATES A LIST OF 16 48 BITS SUBKEYS
        # RUNS PC-1 PERMUTATION - 64 BITS TO 56 BITS
        # SPLITS THE PERMUTATED KEY INTO 2 28 BIT HALVES
        # LEFT SHIFTS THE HALVES FOR 16 TIMES ACCORDING TO LEFT SHIFT TABLE AND COMBINES THEM INTO A LIST 
        # RUNS PC-2 PERMUTATION - 56 BITS TO 48 BITS 
    def DES_sub_key_generation(self,binary_key):
        temp = ""

        # PC-1 PERMUTATION 
        for i in range(len(PC_1)):
            temp += binary_key[PC_1[i]-1]
        binary_key = temp

        # KEY SPLITTING
        L_0 = binary_key[:28]
        R_0 = binary_key[28:]

        # SHIFTING 
        left_rotations = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
        cd_combinations = []

        for i in left_rotations:
            temp = L_0[:i]
            L_0 = L_0[i:] + temp

            temp = R_0[:i]
            R_0 = R_0[i:] + temp
            cd_combinations.append(L_0 + R_0)

        #  PC-2 PERMUTATION 
        generated_sub_keys = []
        for i in range(16):
            temp = ""
            for j in range(len(PC_2)):
                temp += cd_combinations[i][PC_2[j]-1]
            generated_sub_keys.append(temp)

        return generated_sub_keys  
    
    def DES_Operations(self,binary_val,generated_sub_keys):
    # PHASE 2
        # GETTING 64 BIT BLOCKS
        bit_blocks = self.DES_dividing_and_padding(binary_val)

        # GETTING EACH 64 BIT PERMUTATED BY IP TABLE
        permutated_bits = self.DES_initial_permutation(bit_blocks)

    # PHASE 3 
        L_halves,R_halves = self.block_division(permutated_bits) # DIVIDES ALL 64 BIT BLOCKS INTO 2 HALVES

        # RUNS FUNCTION FOR EACH 64 BIT BLOCK'S HALVES 
        # FOR EACH OF THE 64 BIT BLOCK
            # 16 TIMES
                # CALLS THE FUNCTION FOR ROUNDS
            # CALLS FINAL PERMUTATION FUNCTION
            # COMBINES INTO A LIST
            # TURNS INTO A STRING
        processed_bit_blocks = []
        for i in range(len(permutated_bits)):
            # GETTING THE HALVES OF THE CORRESPONDING 64 BIT BLOCK OF THE BINARY VALUE
            left_n = L_halves[i]
            right_n = R_halves[i]
            # RUNNING FUNCTION FOR 16 TIMES 
            for j in range(16):

                left_n, right_n = self.function_computation(left_n, right_n,generated_sub_keys[j])
            
            left_n, right_n = right_n, left_n
            # FINAL PERMUTATION OF L16 AND R16   
            # COMBINING PERMUTATED L16 AND R16 INTO A LIST 
            processed_bit_blocks.append(self.des_final_permutation(left_n,right_n))
    
        # COMBINING THE 64 BITS INTO ONE STRING
        processed_value =""
        for i in range(len(processed_bit_blocks)):

            processed_value += processed_bit_blocks[i]
        
        return processed_value

    # DIVIDES THE BINARY VALUE INTO 64 BIT LONG BLOCKS
    # ADDS PADDING IF NECCESSARY
    # CREATES A LIST 
    def DES_dividing_and_padding(self, binary_val):
        """Divides the binary string into 64-bit blocks and applies PKCS#7 padding properly."""
        
        bit_blocks = []
        
        if not binary_val:  # Handle empty input
            return bit_blocks

        # Convert the binary string into bytes
        original_bytes = bytes(int(binary_val[i:i+8], 2) for i in range(0, len(binary_val), 8))

        block_size = 8  # 8 bytes = 64 bits
        pad_len = block_size - (len(original_bytes) % block_size)

        # Apply PKCS#7 padding only if needed
        if pad_len != block_size:  
            padded_bytes = original_bytes + bytes([pad_len]) * pad_len
        else:
            padded_bytes = original_bytes  # No extra padding needed

        # Convert the padded bytes back to a binary string
        padded_bitstring = ''.join(f"{byte:08b}" for byte in padded_bytes)

        # Split into 64-bit blocks
        for i in range(0, len(padded_bitstring), 64):
            bit_blocks.append(padded_bitstring[i:i+64])

        return bit_blocks


    # RUNS INITIAL PERMUTATION THROUGH IP TABLE ON ALL 64 BITS OF THE BINARY VALUE
    def DES_initial_permutation(self, bit_blocks):    
        permutated_bits = []
        for i in range(len(bit_blocks)):
            temp = ""
            for j in range(len(IP)):
                temp += bit_blocks[i][IP[j]-1]
            permutated_bits.append(temp)
        
        return permutated_bits  

    # DIVIDES ALL PERMUTATED 64 BITS INTO EQUAL HALVES INTO A LIST
    def block_division(self, permutated_bits):
        L_halves = []
        R_halves = []

        for i in range(len(permutated_bits)):
            L_halves.append(permutated_bits[i][:32])
            R_halves.append(permutated_bits[i][32:])

        return L_halves,R_halves

    # ALGORITHM
        # Ln = Rn-1
        # Rn = Ln-1 XOR f(Rn-1,Kn)
    # THIS FUNCTION IS BEING CALLED 16 TIMES BY DES OPERATIONS FUNCTION
    def function_computation(self,L_n_1,R_n_1,Kn):
        # SWAPPING HALVES
        # Ln = Rn-1
        left_n = R_n_1
        # FUNCTION CALL                 f(Rn-1,Kn)
        function_output = self.Rn1_Kn_function(R_n_1,Kn)
        # Rn    = Ln-1            XOR       f(Rn-1,Kn)
        right_n = bin(int(L_n_1,2) ^ int(function_output,2))[2:].zfill(32)
        return left_n, right_n

    # f(Rn-1,Kn)
    # EXPANDS THE 32 BIT Rn-1 TO 48 BITS
    # XOR'S WITH CORRESPONDING 48 BIT KEY VALUE
    # DIVIDES INTO 6 BIT GROUPS
    # SUBSTITUDE BY CORRESBONDING S BOXES AND CREATES 4 BITS LIST 
    # COMBINES ALL 8 FOUR BITS INTO 32 
    # RUNS FUNCTION PERMUTATION ON FINAL 32 BITS
    def Rn1_Kn_function(self,r_n_1,key_i):
        temp = ""
        # EXPENSION
        # 32 BITS TO 48 BITS
        for i in range(len(expension_table)):
            temp += r_n_1[expension_table[i]-1]
        r_n_1 = temp

        # XOR OPERATION WITH KEY_İ
        # GENERATES 48 BITS
        xor_result = bin(int(r_n_1,2) ^ int(key_i,2))[2:].zfill(48) # CONVERT TO INT,IN BASE 2 || ^ : XOR || [2:] : REMOVE 0b PREFIX || BIN : CONVERT TO BINARY

        # SUBSTUTITION
        # DIVIDING INTO 8 6 BITS GROUPS OF THE XOR RESULT 
        six_bit_blocks = []
        for i in range(0,len(xor_result),6):
            six_bit_blocks.append(xor_result[i:i+6])

        four_bit_blocks = []
        
        for i in range(8):
                    # TAKING FIRST BIT AND THE LAST BIT -> ROW NUMBER
                row_pos = six_bit_blocks[i][0]
                row_pos += six_bit_blocks[i][len(six_bit_blocks[i])-1:]

                    # TAKING THE MIDDLE BITS -> COLUMN NUMBER
                col_pos = six_bit_blocks[i][1:len(six_bit_blocks[i])-1]

                row_pos = int(row_pos,2)
                col_pos = int(col_pos,2)

                    # CONVERTING FROM 6 BITS TO 4 BITS THROUGH CORRESPONDING S-BOXES, WRITING INTO LIST IN 4 BITS FORM
                s_box_value = s_box_main[i][row_pos][col_pos]
                four_bit_result  = format(int(s_box_value),'04b')
                four_bit_blocks.append(four_bit_result )
                temp = 0

        # COMBINING ALL FOUR BITS INTO ONE -> 32 BITS
        r_n_1 = ''.join(four_bit_blocks)
    
        # PERMUTATION
        temp = ""
        for i in range(len(f_permutation_table)):
                temp += r_n_1[f_permutation_table[i]-1]
        r_n_1 = temp

        return(r_n_1)

    def des_final_permutation(self,left_n,right_n):
        temp = ""
        combined_halves = left_n + right_n
        for i in range(len(final_permutation_table)):
            temp += combined_halves[final_permutation_table[i]-1]
        combined_halves = temp

        return combined_halves

    def Encrypt_keys(self,generated_key,master_key):
        
        binary_key = self.DES_key_conversion_to_binary(master_key) # TURNS THE KEY TO BINARY

        generated_sub_keys = self.DES_sub_key_generation(binary_key) # GENERATES SUBKEYS

        # GETTING BINARY VERSION OF THE VALUE
        binary_val = ""
        byte_array = bytearray(str(generated_key),'utf-8')

        for j in byte_array:
            binary_val_add = bin(j)[2:].zfill(8)
            binary_val += binary_val_add 
            
        processed_value = self.DES_Operations(binary_val,generated_sub_keys) # STARTS ENCRYPTING 
        processed_value = hex(int(processed_value,2))[2:].zfill(16) # RETURNING ENCRYPTED VALUE AS HEX STRING

        path = "./keys.txt"
        if os.path.isfile(path) == False: # CREATE A .TXT FILE IF NOT EXIST 
            open("keys.txt", "x")
        with open("keys.txt", "a+") as file: # -> APPEND THE KEY TO A NEXT LINE
            file.write(processed_value + "\n")
        pass

    def Decrypt_keys(self,master_key):
        
        binary_key = self.DES_key_conversion_to_binary(master_key) # TURNS THE KEY TO BINARY

        generated_sub_keys = self.DES_sub_key_generation(binary_key) # GENERATES SUBKEYS
        generated_sub_keys.reverse() # REVERSING THE ORDER FOR DECRYPTION 

        connection = sqlite3.connect("Loggs.db")
        cursor = connection.cursor()

        cursor.execute("SELECT row_id FROM decrypted_data ORDER BY row_id DESC")

        try:
            last_line = cursor.fetchone()[0]
        except:
            last_line = 0

        decrypted_keys = []
        try:
            with open("keys.txt", "r") as file: # -> GET THE AMOUNT OF KEYS

                temp = file.readlines()
                lines = temp[last_line:]
                file.seek(0)

                for line in lines:
                    value = line[:-1]
                    # TURNS THE THE VALUE INTO BINARY FOR PROCESSING 
                    binary_val = bin(int(value, 16))[2:].zfill(len(value) * 4)

                    processed_value = self.DES_Operations(binary_val,generated_sub_keys)

                    # Split the binary string into 8-bit chunks (bytes)
                    byte_list = [processed_value[b:b+8] for b in range(0, len(processed_value), 8)]
                    
                    # Convert each 8-bit chunk to an integer, then create a bytes object
                    byte_array = bytes([int(bv, 2) for bv in byte_list])
                    
                    # Decode the bytes object using UTF-8
                    processed_value = byte_array.decode('utf-8')
                    
                    # NO PADDING REMOVAL SINCE ALL KEYS ARE IN MUTLIPLE OF 8 BITS 

                    decrypted_keys.append(processed_value) # WRITES DECRYPTED KEYS INTO A LIST FOR DATABASE DECRYPTION
                lines = len(lines)
            return lines, decrypted_keys
        except FileExistsError:
            print("keys.txt file doesn't Exist")
            exit()
                    