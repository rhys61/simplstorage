To use, first declare your storage classes:



import simplstorage as ss

storage = ss.LocalStorage(password,iterations,salt) #for use in only the single python file

\#or

globalstorage = ss.GlobalStorage(password,iterations,salt) #for use between different files and directories



Here is a list of commands inside each object:



.store(data,handler)

Stores the data using the handler as an identifier to retrieve later. Overwrites the data if already defined, otherwise just appends your new data

in the document. Returns True afterward. You can also give multiple data handler pairs through either tuples or lists.



.retrieve(handler)

Returns the data associated with the handler input. Returns False if the data has been tampered with and None if no handler was found. If handler

is a list or tuple, it will iterate through and return all data in list form.



.exists(handler)

Returns True if there is data with the specified handler, otherwise returns False. If a list is given, it will return a list of the outputs



.delete(handler)

Deletes all data associated with the handler, also accepting lists for multiple handlers.



.deleteall()

Deletes all data related to the storage object.



.pop(handler)

Returns the value(s) stored at handler, and deletes the data after retrieving.



Explanation of how this works:

It stores all the data in a .dat file stored inside programdata, inside the folder called "Python Package Data". The data is stored in sets of

2 lines, line 1 being the handler and line 2 being the encrypted pickled data.

All the data is stored as Fernet encrypted tokens, and decrypted when retrieving, ensuring that the pickled data hasn't been tampered with, as long

as an attacker doesn't get the key used to encrypt the data.



The .deleteall() function loops through all the handlers and if the Fernet doesn't return an invalid token error, it deletes the entry.



The code used to generate the keys used to encrypt the file is the pbkdf2 HMAC, with sha256, with the full file-path being added into the key,

to make any duplicate keys inside programs not interfere, and to make hacking the data harder, as you have to either recreate the file-path, or

code it yourself.



GlobalStorage is the same thing, except it doesn't contain the file-path, allowing for data to be accessed from any python script as long as you have

the correct key.



NOTE:

This was only tested on Windows, so any issues on a different operating system are expected.

