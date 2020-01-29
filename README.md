# Export Transcripts v1.0

Program Input: **accounts.json** file

## **accounts.json file requirements:**

* **interactionType**: 	VALUE NOT NECESSARY, leave blank for both chat & messaging
* **accountNo**: 	  	VALUE REQUIRED
* **startDate**: 	  	VALUE NOT NECESSARY, leave blank for 13 months back from today Format: "%d/%m/%Y %H:%M:%S"
* **endDate**: 		VALUE NOT NECESSARY, leave blank for today's date Format: "%d/%m/%Y %H:%M:%S"
* **app_key**:		VALUE REQUIRED
* **secret**: 		VALUE REQUIRED
* **access_token**: 	  	VALUE REQUIRED
* **access_token_secret**: 	VALUE REQUIRED
* **contentToRetrieve**: 	VALUE NOT NECESSARY, only available for messaging

**accounts.json** file can have multiple accounts to retrieve transcripts from.

**exportTransctipts.py** program will produce a folder and a **logs.txt** file once it has finished extracting transcripts. The folder will contain all the transcripts.