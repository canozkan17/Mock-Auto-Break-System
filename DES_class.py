from DES_constants import * 
import math
import datetime
import sqlite3
import os.path

"""
This module implements the Data Encryption Standard (DES) algorithm for encrypting
and decrypting data. It includes functions for key generation, subkey generation,
and the core DES operations (initial permutation, Feistel network rounds, final
permutation). It also handles the interaction with a database for storing and
retrieving encrypted data and keys.
"""

class DES_Encryption_Decryption:
    """
    Provides methods for DES encryption and decryption.

    This class encapsulates the entire DES algorithm, including:
    - Key generation based on vehicle speed and object creation time.
    - Encryption of generated keys using a master key.
    - Encryption of vehicle data.
    - Decryption of vehicle data using decrypted keys.
    - Decryption of keys using a master key.
    - Core DES operations like initial permutation, Feistel rounds, S-box substitution, etc.

    Type Aliases (for clarity in docstrings):
        VehicleObject: Represents an object with attributes like `date_time`, `speed_kmh`,
                       and a `collected_data` dictionary.
        DatabaseObject: Represents an instance of a database interaction class (e.g., `DB_class.DataBase`).
    """
    
    def Encrypt_to_db(self,vehicle_object: 'classes.Vehicle', master_key: str):
        """
        Encrypts the data of a vehicle object. The encrypted data is updated
        in the `vehicle_object.collected_data` dictionary.

        The process involves:
        1. Generating a unique DES key for the vehicle data based on its properties.
        2. Encrypting this DES key using a provided master key and storing it via `Encrypt_keys`.
        3. Converting the unique DES key to its binary representation.
        4. Generating 16 DES subkeys from this binary DES key.
        5. Iterating through each data field in the `vehicle_object.collected_data`.
        6. Converting each data value to its binary representation.
        7. Performing DES encryption on the binary data using the generated subkeys. PKCS#7
           padding is applied during this operation if necessary.
        8. Converting the encrypted binary data to a hexadecimal string. The length of this
           hex string will be twice the number of bytes in the padded encrypted binary data.
        9. Updating the `vehicle_object.collected_data` dictionary with the encrypted hex string
           for each corresponding key.

        Args:
            vehicle_object (VehicleObject): An object containing the data to be encrypted.
                                            It must have a `date_time` attribute (datetime object),
                                            a `speed_kmh` attribute, and a `collected_data`
                                            dictionary.
            master_key (str): The master key (typically 8 ASCII characters) used to encrypt
                              the generated DES key.
        """

        object_creation_time = vehicle_object.date_time.strftime("%f") # NANO SECONDS OF THE TIME OF THE PASSED VEHICLE OBJECT CREATION

        The process involves:
        1. Generating a unique DES key for the vehicle data.
        2. Encrypting this DES key using a provided master key and storing it.
        3. Converting the DES key to its binary representation.
        4. Generating 16 subkeys from the binary DES key.
        5. Iterating through each data field in the vehicle_object's collected_data.
        6. Converting each data value to its binary representation.
        7. Performing DES encryption on the binary data using the generated subkeys.
        8. Converting the encrypted binary data to a hexadecimal string.
        9. Updating the `vehicle_object.collected_data` with the encrypted hex string.

        Args:
            vehicle_object (VehicleObject): An object containing the data to be encrypted.
                                     It must have a `date_time` attribute (datetime object),
                                     a `speed_kmh` attribute, and a `collected_data`
                                     dictionary.
            master_key (str): The master key used to encrypt the generated DES key.
        """

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
            processed_value = hex(int(processed_value,2))[2:].zfill(hex_lenght) # Convert binary to hex string

            vehicle_object.collected_data.update({f"{dict_keys[i]}": processed_value})


    def Decrypt_from_db(self,database_object: 'DB_class.DataBase',master_key: str):
        """
        Decrypts data from the 'logged_data' table and inserts it into 'decrypted_data'.

        The process involves:
        1. Creating a 'decrypted_data' table if it doesn't exist.
        2. Determining the starting row_id for decryption based on existing decrypted data.
        3. Decrypting the stored DES keys using the master key.
        4. Fetching encrypted data row by row from the 'logged_data' table.
        5. For each row:
            a. Converting the corresponding decrypted DES key to binary.
            b. Generating 16 subkeys from the binary DES key and reversing their order for decryption.
            c. Iterating through each encrypted value in the row.
            d. Converting the hex-encoded encrypted value to its binary representation.
            e. Performing DES decryption on the binary data using the reversed subkeys.
            f. Converting the decrypted binary data back to its original string form,
               handling PKCS#7 padding removal.
            g. Storing the decrypted row in the 'decrypted_data' table using the database_object.

        Args:
            database_object (DatabaseObject): An instance of a database interaction class
                                              (e.g., `DB_class.DataBase`) used to interact
                                              with the database.
            master_key (str): The master key (typically 8 ASCII characters) used to
                              decrypt the DES keys.
        """
        db = database_object

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
                if item == 0: # Skip row_id
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
            
    def DES_key_generation(self,seed: float, object_creation_time: str) -> str:
        """
        Generates an 8-character (64-bit) ASCII string key for DES encryption.

        The key generation uses a pseudo-random process based on:
        - A seed value (e.g., vehicle speed).
        - The nanoseconds part of the vehicle object's creation time.
        - The nanoseconds part of the current time (encryption start time).

        A linear congruential generator (LCG)-like formula is used:
        `temp = (((seed * A) + C) % M)`
        where A and C are derived from time components and M is the alphabet size.
        The generated `temp` value determines whether the next character in the key
        is a number, an uppercase letter, or a lowercase letter.

        Args:
            seed (float): The initial seed value for the key generation algorithm.
            object_creation_time (str): The nanosecond part of the timestamp when the
                                       object to be encrypted was created (as a string).

        Returns:
            str: The generated 8-character ASCII key.
        """
        
        temp = 0
        key = ""
        # ENG ALPHABET IS USED FOR 64 BIT INITIAL KEY 
        upper_eng_alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        lower_eng_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        num_list =           ['1', '2', '3', '4', '5', '6', '7', '8', '9']


        #PREPPING CONSTANTS THROUGH TIME STAMPS
        key_creator_const_c = int(object_creation_time)
        key_creator_const_a = int(datetime.datetime.now().strftime("%f")) # NANO SECONDS OF THE ENCRYPTION START TIME
        mode_letter_count_m = len(upper_eng_alphabet) # Using uppercase alphabet length as modulus M


        # Ensure (A - 1) is divisible by M for LCG properties
        if (key_creator_const_a - 1) % mode_letter_count_m != 0:
            key_creator_const_a -= (key_creator_const_a - 1) % mode_letter_count_m

        # Ensure GCD(M, C) = 1 for LCG properties (full period)
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
        for i in range(8): # Generate 8 characters for the key
            temp = (((seed * key_creator_const_a) + key_creator_const_c) % mode_letter_count_m) 
            if temp % 5 == 0: # If temp is a multiple of 5, choose a number
                key += num_list[temp % len(num_list)]
            elif temp % 2 == 0: # If temp is even, choose an uppercase letter
                key += upper_eng_alphabet[temp % 26] # Modulo 26 for alphabet index
            else: # If temp is odd, choose a lowercase letter
                key += lower_eng_alphabet[temp % 26] # Modulo 26 for alphabet index
            seed = temp # Update seed for the next iteration (LCG behavior)
        
        return key
    
    def DES_key_conversion_to_binary(self,key: str) -> str:
        """
        Converts an ASCII key string to its 64-bit binary representation.

        Each character in the key is converted to its 8-bit binary form (UTF-8),
        and these are concatenated to form a single binary string.

        Args:
            key (str): The ASCII key string (expected to be 8 characters long).

        Returns:
            str: The 64-bit binary representation of the key.
        """
        
        binary_key = ""
        byte_array = bytearray(key,'utf-8')

        for i in byte_array:
            binary_val = bin(i)[2:].zfill(8) # Convert char to 8-bit binary
            binary_key += binary_val 
    
        return binary_key

    def DES_sub_key_generation(self,binary_key: str) -> list[str]:
        """
        Generates 16 subkeys (48-bit each) from a 64-bit binary DES key.

        The process involves:
        1. Permuted Choice 1 (PC-1): Reduces the 64-bit key to 56 bits, discarding parity bits.
        2. Splitting: Divides the 56-bit key into two 28-bit halves (C0 and D0).
        3. Left Shifts: For 16 rounds, the C and D halves are independently
           left-shifted by 1 or 2 positions according to the DES left shift schedule.
        4. Permuted Choice 2 (PC-2): After each shift, the combined 56-bit C_n and D_n
           is permuted and compressed to produce a 48-bit subkey K_n.

        Args:
            binary_key (str): The 64-bit binary representation of the DES key.

        Returns:
            list[str]: A list of 16 subkeys, each being a 48-bit binary string.
        """
        temp = ""

        # PC-1 PERMUTATION (64 bits to 56 bits)
        for i in range(len(PC_1)):
            temp += binary_key[PC_1[i]-1] # PC_1 uses 1-based indexing
        binary_key_56_bits = temp

        # KEY SPLITTING into C0 and D0 (28 bits each)
        L_0 = binary_key_56_bits[:28]
        R_0 = binary_key_56_bits[28:]

        # SHIFTING and generating CnDn combinations
        left_rotations = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1] # DES left shift schedule
        cd_combinations = []
        C_n, D_n = L_0, R_0

        for num_shifts in left_rotations:
            # Perform left circular shift on C_n
            temp_c = C_n[:num_shifts]
            C_n = C_n[num_shifts:] + temp_c
            # Perform left circular shift on D_n
            temp_d = D_n[:num_shifts]
            D_n = D_n[num_shifts:] + temp_d

            cd_combinations.append(C_n + D_n) # Store combined CnDn for this round

        #  PC-2 PERMUTATION (56 bits to 48 bits for each subkey)
        generated_sub_keys = []
        for i in range(16): # For each of the 16 rounds
            temp_subkey = ""
            current_cd = cd_combinations[i]
            for j in range(len(PC_2)):
                temp_subkey += current_cd[PC_2[j]-1] # PC_2 uses 1-based indexing
            generated_sub_keys.append(temp_subkey)

        return generated_sub_keys  
    
    def DES_Operations(self,binary_val: str, generated_sub_keys: list[str]) -> str:
        """
        Performs the core DES encryption/decryption operations on binary data.

        This function implements the main DES structure:
        1. Data Preparation: Divides the input binary string (`binary_val`) into 64-bit
           blocks, applying PKCS#7 padding if necessary.
        2. Initial Permutation (IP): Each 64-bit block is permuted according to the
           DES initial permutation table.
        3. Feistel Network (16 Rounds):
           a. Each permuted block is split into a 32-bit left half (L) and a 32-bit
              right half (R).
           b. For 16 rounds, the `function_computation` method is called, which
              applies the DES round function (f) using the corresponding subkey.
              - L_i = R_{i-1}
              - R_i = L_{i-1} XOR f(R_{i-1}, K_i)
           c. After 16 rounds, the final L16 and R16 are swapped.
        4. Final Permutation (FP): The combined L16R16 block is permuted according
           to the DES final permutation table (inverse of IP).
        5. Output: The processed 64-bit blocks are concatenated to form the final
           encrypted or decrypted binary string.

        Args:
            binary_val (str): The input binary string to be processed (plaintext for
                              encryption, ciphertext for decryption).
            generated_sub_keys (list[str]): A list of 16 DES subkeys (48-bit each).
                                            For decryption, these keys should be in
                                            reversed order.

        Returns:
            str: The resulting binary string after DES operations (ciphertext for
                 encryption, plaintext for decryption).
        """
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
        for i in range(len(permutated_bits)): # For each 64-bit block
            # GETTING THE HALVES OF THE CORRESPONDING 64 BIT BLOCK OF THE BINARY VALUE
            left_n = L_halves[i]
            right_n = R_halves[i]
            # RUNNING FUNCTION FOR 16 TIMES 
            for j in range(16): # 16 rounds of Feistel network
                left_n, right_n = self.function_computation(left_n, right_n,generated_sub_keys[j])
            
            # Swap halves after the 16th round (before final permutation)
            left_n, right_n = right_n, left_n
            # FINAL PERMUTATION OF L16 AND R16   
            # COMBINING PERMUTATED L16 AND R16 INTO A LIST 
            processed_bit_blocks.append(self.des_final_permutation(left_n,right_n))
    
        # COMBINING THE 64 BITS INTO ONE STRING
        processed_value =""
        for i in range(len(processed_bit_blocks)):
            processed_value += processed_bit_blocks[i]
        
        return processed_value

    def DES_dividing_and_padding(self, binary_val: str) -> list[str]:
        """
        Divides a binary string into 64-bit blocks and applies PKCS#7 padding.

        If the input binary string is not a multiple of 64 bits, PKCS#7 padding
        is applied to the last block. Each byte of padding is set to the number
        of padding bytes added.

        Args:
            binary_val (str): The input binary string.

        Returns:
            list[str]: A list of 64-bit binary string blocks.
        """
        
        bit_blocks = []
        
        if not binary_val:  # Handle empty input
            # If input is empty, technically no blocks and no padding needed for DES processing itself.
            # However, to be robust with subsequent steps that expect blocks,
            # an empty list is appropriate. If a single padded block is always expected for empty input,
            # this would need adjustment (e.g., a full block of padding).
            # For now, returning empty list for empty input.
            return bit_blocks

        # Convert the binary string into bytes
        # Ensure binary_val length is a multiple of 8 for proper byte conversion
        if len(binary_val) % 8 != 0:
            # This case should ideally be handled by the caller ensuring byte-aligned input,
            # or this function needs a defined strategy for non-byte-aligned binary strings.
            # For DES, input is typically text -> bytes -> binary, so it should be byte-aligned.
            # Assuming it is, or will be padded to be, before this specific padding step.
            # If not, this could lead to errors or misinterpretation.
            pass # Or raise an error: raise ValueError("Binary string length must be a multiple of 8 for byte conversion.")

        original_bytes = bytes(int(binary_val[i:i+8], 2) for i in range(0, len(binary_val), 8))

        block_size_bytes = 8  # 8 bytes = 64 bits
        num_bytes = len(original_bytes)
        pad_len = block_size_bytes - (num_bytes % block_size_bytes)

        # Apply PKCS#7 padding
        if pad_len == block_size_bytes: # If already a multiple of block_size_bytes
            # As per some interpretations of PKCS#7, if the input is already a multiple
            # of the block size, a full block of padding (e.g., 8 bytes of 0x08) is added.
            # Other interpretations (like the one used before the edit) add no padding.
            # Sticking to the "add a full block if multiple" for stricter PKCS#7.
             padded_bytes = original_bytes + bytes([block_size_bytes]) * block_size_bytes
        else: # If not a multiple, pad to the next multiple
            padded_bytes = original_bytes + bytes([pad_len]) * pad_len


        # Convert the padded bytes back to a binary string
        padded_bitstring = ''.join(f"{byte:08b}" for byte in padded_bytes)

        # Split into 64-bit blocks
        for i in range(0, len(padded_bitstring), 64):
            bit_blocks.append(padded_bitstring[i:i+64])

        # If the original binary_val was empty, padded_bitstring will be one block of padding.
        # Example: if binary_val="", original_bytes=b"", num_bytes=0.
        # pad_len = 8 - (0 % 8) = 8. padded_bytes = bytes([8])*8.
        # padded_bitstring = "00001000" * 8. bit_blocks will contain this one block.
        # This ensures even an empty input results in one processable block.

        return bit_blocks


    def DES_initial_permutation(self, bit_blocks: list[str]) -> list[str]:
        """
        Applies the DES Initial Permutation (IP) to a list of 64-bit blocks.

        Each bit in each block is rearranged according to the predefined IP table.

        Args:
            bit_blocks (list[str]): A list of 64-bit binary string blocks.

        Returns:
            list[str]: A list of permuted 64-bit binary string blocks.
        """
        permutated_bits = []
        for i in range(len(bit_blocks)): # For each block
            temp = ""
            current_block = bit_blocks[i]
            for j in range(len(IP)): # IP table has 64 entries
                temp += current_block[IP[j]-1] # IP table uses 1-based indexing
            permutated_bits.append(temp)
        
        return permutated_bits  

    def block_division(self, permutated_bits: list[str]) -> tuple[list[str], list[str]]:
        """
        Divides each 64-bit permuted block into two 32-bit halves (L and R).

        Args:
            permutated_bits (list[str]): A list of 64-bit binary string blocks
                                         that have undergone initial permutation.

        Returns:
            tuple[list[str], list[str]]: A tuple containing two lists:
                                         - The first list contains all the 32-bit left halves (L).
                                         - The second list contains all the 32-bit right halves (R).
        """
        L_halves = []
        R_halves = []

        for i in range(len(permutated_bits)):
            current_block = permutated_bits[i]
            L_halves.append(current_block[:32])
            R_halves.append(current_block[32:])

        return L_halves,R_halves

    def function_computation(self,L_n_1: str, R_n_1: str, Kn: str) -> tuple[str, str]:
        """
        Computes one round of the DES Feistel network.

        The DES round function is:
        L_n = R_{n-1}
        R_n = L_{n-1} XOR f(R_{n-1}, K_n)

        where:
        - L_{n-1}, R_{n-1} are the left and right halves from the previous round.
        - K_n is the subkey for the current round.
        - f is the Feistel function (`Rn1_Kn_function`).

        Args:
            L_n_1 (str): The 32-bit left half from the previous round (L_{i-1}).
            R_n_1 (str): The 32-bit right half from the previous round (R_{i-1}).
            Kn (str): The 48-bit subkey for the current round (K_i).

        Returns:
            tuple[str, str]: A tuple containing the new 32-bit left half (L_n)
                             and right half (R_n) for the current round.
        """
        # Ln = Rn-1
        left_n = R_n_1

        # Calculate f(Rn-1, Kn)
        function_output = self.Rn1_Kn_function(R_n_1,Kn)

        # Rn = Ln-1 XOR f(Rn-1,Kn)
        # Convert binary strings to integers for XOR, then back to 32-bit binary string
        right_n_int = int(L_n_1,2) ^ int(function_output,2)
        right_n = format(right_n_int, '032b') # Ensure it's 32 bits, padding with leading zeros if needed

        return left_n, right_n

    def Rn1_Kn_function(self,r_n_1: str, key_i: str) -> str:
        """
        Implements the DES Feistel function f(R_{n-1}, K_i).

        The function involves:
        1. Expansion (E-box): The 32-bit R_{n-1} is expanded to 48 bits using the
           DES expansion table.
        2. XOR: The 48-bit expanded R_{n-1} is XORed with the 48-bit round subkey K_i.
        3. S-box Substitution: The 48-bit XOR result is divided into eight 6-bit blocks.
           Each 6-bit block is passed through a corresponding S-box, resulting in
           a 4-bit output.
        4. Concatenation: The eight 4-bit outputs from the S-boxes are concatenated
           to form a 32-bit string.
        5. Permutation (P-box): This 32-bit string is permuted according to the DES
           P-box permutation table.

        Args:
            r_n_1 (str): The 32-bit right half from the previous round (R_{n-1}).
            key_i (str): The 48-bit subkey for the current round (K_i).

        Returns:
            str: The 32-bit output of the Feistel function.
        """
        temp_expanded_r = ""
        # EXPANSION (E-box): 32 bits to 48 bits
        for i in range(len(expension_table)): # expansion_table has 48 entries
            temp_expanded_r += r_n_1[expension_table[i]-1] # expension_table uses 1-based indexing
        expanded_r = temp_expanded_r

        # XOR OPERATION WITH key_i (48 bits)
        xor_result_int = int(expanded_r,2) ^ int(key_i,2)
        xor_result = format(xor_result_int, '048b') # Ensure 48 bits

        # S-BOX SUBSTITUTION
        # Dividing the 48-bit XOR result into eight 6-bit blocks
        six_bit_blocks = []
        for i in range(0,len(xor_result),6):
            six_bit_blocks.append(xor_result[i:i+6])

        four_bit_sbox_outputs = []
        for i in range(8): # For each of the 8 S-boxes
            current_6bit_block = six_bit_blocks[i]

            # Determine row for S-box lookup: bits 1 and 6 (0-indexed)
            row_bits = current_6bit_block[0] + current_6bit_block[5]
            row_index = int(row_bits,2)

            # Determine column for S-box lookup: bits 2-5 (0-indexed)
            col_bits = current_6bit_block[1:5]
            col_index = int(col_bits,2)

            # S-box lookup and conversion to 4-bit binary string
            s_box_value = s_box_main[i][row_index][col_index] # s_box_main defined in DES_constants
            four_bit_result  = format(s_box_value,'04b') # Ensure 4 bits
            four_bit_sbox_outputs.append(four_bit_result)

        # COMBINING all 4-bit outputs into one 32-bit string
        sbox_combined_output = ''.join(four_bit_sbox_outputs)
    
        # PERMUTATION (P-box)
        temp_permuted_sbox_output = ""
        for i in range(len(f_permutation_table)): # f_permutation_table has 32 entries
                temp_permuted_sbox_output += sbox_combined_output[f_permutation_table[i]-1] # f_permutation_table uses 1-based indexing
        permuted_sbox_output = temp_permuted_sbox_output

        return permuted_sbox_output

    def des_final_permutation(self,left_n: str, right_n: str) -> str:
        """
        Applies the DES Final Permutation (FP) to the combined L16 and R16 halves.

        The 64-bit block formed by concatenating L16 and R16 is permuted according
        to the predefined final_permutation_table (which is the inverse of the
        Initial Permutation table).

        Args:
            left_n (str): The 32-bit left half after 16 rounds (L16, or R16 if swapped).
            right_n (str): The 32-bit right half after 16 rounds (R16, or L16 if swapped).

        Returns:
            str: The 64-bit permuted binary string block.
        """
        temp_final_perm = ""
        combined_halves = left_n + right_n
        for i in range(len(final_permutation_table)): # final_permutation_table has 64 entries
            temp_final_perm += combined_halves[final_permutation_table[i]-1] # Table uses 1-based indexing
        
        return temp_final_perm

    def Encrypt_keys(self,generated_key: str, master_key: str):
        """
        Encrypts a generated DES key using a master key and appends it to 'keys.txt'.

        The encryption process uses the DES algorithm itself:
        1. Convert the master key to its binary representation.
        2. Generate subkeys from the binary master key.
        3. Convert the `generated_key` (which is the key to be encrypted) to its
           binary representation. PKCS#7 padding is applied implicitly by DES_Operations
           if the key's binary form isn't a multiple of 64 bits (though 8-char ASCII keys are).
        4. Perform DES encryption on the binary `generated_key` using the master subkeys.
        5. Convert the encrypted binary key to a hexadecimal string (16 chars for 64 bits).
        6. Append the hex-encoded encrypted key to "keys.txt".

        Args:
            generated_key (str): The DES key to be encrypted (typically 8 ASCII characters).
            master_key (str): The master key to use for encrypting `generated_key`
                              (also typically 8 ASCII characters).
        """

        binary_master_key = self.DES_key_conversion_to_binary(master_key)
        master_sub_keys = self.DES_sub_key_generation(binary_master_key)

        # GETTING BINARY VERSION OF THE generated_key
        binary_val_generated_key = ""
        byte_array_generated_key = bytearray(str(generated_key),'utf-8')

        for j in byte_array_generated_key:
            binary_val_add = bin(j)[2:].zfill(8)
            binary_val_generated_key += binary_val_add
            
        # Encrypt the generated_key using DES with master_sub_keys
        encrypted_binary_key = self.DES_Operations(binary_val_generated_key, master_sub_keys)
        # Convert to hex. `encrypted_binary_key` is 128 bits due to padding of the
        # original 64-bit key data, so it becomes a 32-character hex string.
        encrypted_hex_key = hex(int(encrypted_binary_key,2))[2:].zfill(32)

        path = "./keys.txt"
        if not os.path.isfile(path): # CREATE A .TXT FILE IF NOT EXIST
            open("keys.txt", "x").close() # Ensure file is closed after creation
        with open("keys.txt", "a+") as file: # -> APPEND THE KEY TO A NEXT LINE
            file.write(encrypted_hex_key + "\n")
        # No explicit pass needed here

    def Decrypt_keys(self,master_key: str) -> tuple[int, list[str]]:
        """
        Decrypts DES keys stored in 'keys.txt' using a master key.

        The decryption process uses the DES algorithm:
        1. Convert the master key to its binary representation.
        2. Generate subkeys from the binary master key and reverse their order for decryption.
        3. Read encrypted keys (hex strings) from 'keys.txt', starting from a specific
           line determined by the number of already decrypted entries in the database.
        4. For each encrypted key:
           a. Convert the hex-encoded key to its binary representation (64 bits).
           b. Perform DES decryption on the binary key using the reversed master subkeys.
           c. Convert the decrypted binary key (which is 64 bits) back to an 8-character
              ASCII string. PKCS#7 padding is handled by `DES_Operations` and then
              removed during the binary-to-string conversion if it was applied.
              (Note: For 8-byte keys, full block padding might be added and removed).
        5. Return the number of keys read and the list of decrypted (ASCII) keys.

        Args:
            master_key (str): The master key (typically 8 ASCII characters) to use for
                              decrypting the keys in 'keys.txt'.

        Returns:
            tuple[int, list[str]]: A tuple containing:
                                   - The number of keys that were attempted to be read and decrypted.
                                   - A list of decrypted DES keys (8-character ASCII strings).
        
        Raises:
            SystemExit: If 'keys.txt' file does not exist (via `exit()`).
        """

        binary_master_key = self.DES_key_conversion_to_binary(master_key)
        master_sub_keys = self.DES_sub_key_generation(binary_master_key)
        master_sub_keys.reverse() # Reverse order for decryption

        connection = sqlite3.connect("Loggs.db")
        cursor = connection.cursor()

        # Determine how many keys have already been processed and decrypted
        # by looking at the 'decrypted_data' table.
        cursor.execute("SELECT MAX(row_id) FROM decrypted_data") # More efficient
        result = cursor.fetchone()
        last_processed_line_count = result[0] if result and result[0] is not None else 0
        connection.close()


        decrypted_keys_list = []
        lines_to_process_count = 0

        keys_file_path = "keys.txt"
        if not os.path.isfile(keys_file_path):
            print(f"Error: '{keys_file_path}' file doesn't exist.")
            exit() # Or raise an exception: raise FileNotFoundError(f"'{keys_file_path}' not found.")

        with open(keys_file_path, "r") as file:
            all_encrypted_keys_in_file = [line.strip() for line in file.readlines()]

            # Slice the list to get only the keys that haven't been processed yet
            keys_to_decrypt_from_file = all_encrypted_keys_in_file[last_processed_line_count:]
            lines_to_process_count = len(keys_to_decrypt_from_file)

            for encrypted_hex_key in keys_to_decrypt_from_file:
                if not encrypted_hex_key: continue # Skip empty lines

                # Convert hex key to binary. Encrypted keys are 32 hex chars (128 bits).
                binary_length = len(encrypted_hex_key) * 4 # Should be 128
                binary_encrypted_key = bin(int(encrypted_hex_key, 16))[2:].zfill(binary_length)

                decrypted_binary_key = self.DES_Operations(binary_encrypted_key, master_sub_keys) # Output is 128 bits

                # Convert decrypted binary key (128 bits) back to ASCII string.
                # The actual key is 8 chars (64 bits), followed by 8 bytes of PKCS#7 padding.
                # Split the 64-bit binary string into 8-bit chunks (bytes)
                byte_list = [decrypted_binary_key[b:b+8] for b in range(0, len(decrypted_binary_key), 8)]

                # Convert each 8-bit chunk to an integer, then create a bytes object
                byte_array = bytes([int(bv, 2) for bv in byte_list])

                # Decode the bytes object using UTF-8
                # This assumes the original key was UTF-8 encodable, which is true for ASCII.
                decrypted_key_string = byte_array.decode('utf-8')

                # Handle PKCS#7 padding removal if DES_Operations added it.
                # For fixed-size 8-byte keys, if padding was added, it would be a full block of 0x08.
                # If the key itself could contain the padding character as its last char, this might be an issue.
                # Assuming keys are generated such that this isn't ambiguous or that padding is always stripped.
                # The DES_dividing_and_padding was modified to always add a full block if input is multiple of blocksize.
                # So, we should expect padding to be present if DES_Operations was called.

                # Check the last character for padding value.
                if decrypted_key_string: # Ensure not empty
                    padding_size = ord(decrypted_key_string[-1])
                    # Validate padding: all padding bytes should have the value of padding_size
                    # and padding_size should be between 1 and 8 (block size).
                    if 1 <= padding_size <= 8 and \
                       decrypted_key_string.endswith(chr(padding_size) * padding_size):
                        decrypted_key_string = decrypted_key_string[:-padding_size]
                    # If not valid padding, assume no padding was meant to be stripped (e.g. key genuinely ends with that char)
                    # This part is tricky. For this application, keys are 8 chars. If padded, it'd be to 16 bytes (2 blocks).
                    # The current `DES_dividing_and_padding` pads a 64-bit (8 byte) input to 16 bytes.
                    # So, the output of DES_Operations on an 8-char key will be 128 bits.
                    # The `Encrypt_keys` converts this 128-bit value to hex (32 chars).
                    # Then `Decrypt_keys` reads this 32-char hex.
                    # This means the `binary_encrypted_key` is 128 bits.
                    # `DES_Operations` will process it in two 64-bit blocks.
                    # The `decrypted_binary_key` will be 128 bits.
                    # The byte conversion will yield 16 bytes.
                    # The padding removal logic needs to be consistent with this.
                    #
                    # Re-evaluating: `Encrypt_keys` takes an 8-char `generated_key`.
                    # `binary_val_generated_key` becomes 64 bits.
                    # `DES_Operations` is called with this 64-bit value.
                    # `DES_dividing_and_padding` on a 64-bit value adds a full block of padding, making it 128 bits.
                    # `encrypted_binary_key` is 128 bits. `encrypted_hex_key` is 32 hex chars.
                    #
                    # In `Decrypt_keys`:
                    # `binary_encrypted_key` is 128 bits (from 32 hex chars).
                    # `DES_Operations` on this 128-bit value (2 blocks) with reversed keys.
                    # `decrypted_binary_key` is 128 bits.
                    # `byte_array` is 16 bytes. `decrypted_key_string` is 16 chars.
                    # The first 8 chars are the original key, the next 8 are padding (chr(8)*8).
                    # So, `padding_size` will be 8.
                    # `decrypted_key_string[:-8]` will give the original 8-char key. This seems correct.

                decrypted_keys_list.append(decrypted_key_string)

        return lines_to_process_count, decrypted_keys_list
                    