### 2.1.3 Business Rules
An iBuy user must be able to upload attachments, which are stored in Azure Blob Storage and scanned for malware using Microsoft Defender for Cloud. Clean attachments can be accessed publicly or by authorized users through Role-Based and Attribute-Based Access Control (RBAC and ABAC) and secure, obfuscated URIs.



### 2.1.4 Use Case and Process Flow Diagrams

To provide a secure, efficient, and reliable mechanism for uploading, scanning, storing, linking, and sharing attachments with requisition between the iBuy application and Harmony. This ensures that attachments are malware-free, properly linked to requisitions, and accessible only to authorized users or via a secure public API, with URLs returned only if the attachments pass the malware scan.

#### 2.1.4.1 Use Case
**Uploading, Linking, and Sharing Attachments with Requisition**

#### 2.1.4.2 Actors
- **iBuy User**: A user who interacts with the iBuy application to manage tasks. They can upload and retrieve attachments, as well as submit and manage requisition.


- **Harmony User**: A user who retrieves attachments associated with requisition forms from Harmony.
- **External Third-Party**: External users or systems accessing the attachments through a secure public API.
- **System Components**: iBuy Application, Azure Blob Storage, Microsoft Defender for Storage, Oracle Integration Cloud (OIC), Harmony API, Retrieval Function App, Cosmos DB, Public API.

#### 2.1.4.3 Purpose
To provide a secure, efficient, and reliable mechanism for uploading, scanning, storing, linking, and sharing attachments with requisition between the iBuy application and Harmony. This ensures that users can only proceed with requisition forms once the attachments are confirmed to be malware-free and their URLs are securely provided.

#### 2.1.4.4 Process Flow

##### 2.1.4.4.1 Attachment Upload and Blob Storage

1. **User Uploads Attachment**:
   - The iBuy user uploads an attachment via the iBuy web application using an upload form.

2. **Save in Blob Storage**:
   - The iBuy application calls the Attachment Upload API (`POST /api/attachments`).
   - The API stores the uploaded attachment in Azure Blob Storage in a dedicated container.
   - A unique URI is generated for the stored attachment.

3. **Hold Submission Pending Malware Scan**:
   - The API does not immediately return the URI to the user.
   - The URI is returned to the frontend application but not accessible to the user, pending the outcome of the Defender scan.
   - The user cannot proceed to submit out the requisition form until the malware scan is completed.

##### 2.1.4.4.2 Malware Scanning and Event Notification


4. **Perform Malware Scan**:
   - Microsoft Defender for Storage performs a malware scan on the uploaded attachment.


5. **Event Notification**:
   - Microsoft Defender for Storage sends the scan result to Azure Event Grid.
   - An Azure Function subscribes to Event Grid and processes the scan result.

6. **Process Scan Results**:
   - If the attachment is clean:
     - The Azure Function write  the attachment's status in the database to indicate it is safe.

     - The iBuy application updates the user, confirming that the attachment is available and provides the secure URL.
     - The user can now proceed to fill out and submit the requisition form.
   - If the attachment is infected:
     - The attachment is deleted from Azure Blob Storage and logged for auditing purposes.
     -  Once the file deletion is confirmed, update the Defender for Storage alert status to "Closed"
     - An alert is raised, and the iBuy application is notified that the upload failed due to malware, prompting them to retry with a different file.
     - The user can proceed with the requisition, but they will be notified that the attachment has been deleted and is no longer available.

##### 2.1.4.4.3 Linking Attachment to Requisition
7. **User Frontend Handling Callback Function**:
   - When the user uploads a file, the frontend sends a request to the backend upload API.
   - Upon a successful asynchronous response, the frontend receives a unique `scanId` and initializes a polling process using a callback URL.
   - Every 5 seconds, the frontend pings the callback URL with the `scanId` to check if the uploaded file has been successfully scanned.
   - Once the scan is complete, the callback URL returns the payload to the frontend which include  an internal and an external retrieval URL for accessing the attachments:
     - **Internal Retrieval URL:** This URL is intended for use within the organization's network and provides direct access to the scan results.
     - **External Retrieval URL:** This URL allows access to the scan results from outside the organization's network, ensuring secure and controlled retrieval of attachments.

8. **User Fills Requisition**:
   - Once the attachment is confirmed clean and the secure URL is returned, the user can proceed to fill out and submit the requisition form in the iBuy application.
   - The requisition form includes the URIs of the successfully scanned attachments.

9. **Store Requisition and Attachment Links**:
   - The iBuy application saves the requisition form details and associates the attached URIs in the database.
   - Each requisition record in the database contains references to the linked attachment URIs, specifying the attachment level (e.g., header or line item level).

![image.png](/.attachments/image-5b4b4795-9b8f-4300-a44c-146379d663b8.png)

_Figure 1_


##### 2.1.4.4.4 Data Transfer to Harmony

10. **Data Transfer to Harmony**:
    - An Azure Function will directly call the Harmony API with the appropriate payload.
    - The Harmony API creates a record in Harmony, including an obfuscated URI that points to the attachment in Azure Blob Storage.


##### 2.1.4.4.5 Attachment Retrieval Url

11. **Attachment Status URL**:
    - When the user uploads an attachment, the frontend receives a unique `scanId` and a status polling URL from the backend.
    - The frontend uses this polling URL to check the scan status at regular intervals (every 5 seconds).

12. **Polling and Retrieving Attachment**:
    - The frontend periodically pings the provided status polling URL with the `scanId` to check if the scan is complete.
    - Once the scan is completed, the polling response includes an obfuscated URI for retrieving the scanned attachment.



##### 2.1.4.4.6 Public API for Attachment URL Retrieval

14. **Public API Request**:
    - External third-party users or systems can request the attachment URL by calling the Public API (`GET /public-api/attachments/{attachmentId}`).

15. **Validate**:
    - The Public API does not require validation of the requestor’s access permissions.However, rate limiting will be enforced to control the frequency of requests. 
 

16. **Return Attachment URL**:
    - The Public API returns a payload containing the attachment details, including the GUID and any relevant metadata.
    - If the request is invalid or there is an issue with accessing the attachment, an error message will be returned..

![image.png](/.attachments/image-3c010a82-367d-4669-9e6f-e9eb4bbecac3.png)

_Figure 2_



### 2.1.5 User access requirements

To ensure the security and integrity of the attachment management process, it is essential to implement user access controls. These controls include Role-Based Access Control (RBAC), Attribute-Based Access Control (ABAC), and secure handling of attachment URIs..

Are there any additional user access requirements for the feature?


## 2.2 Harmony Design Documents

**NOTE**: Harmony functional + technical spec may be one combined document.

### 2.2.1 Harmony Functional design Document

Provide a link to the Harmony functional design documentation (if required)
[Harmony functional&technical doc](https://ssecom.sharepoint.com/:w:/r/teams/iBuyCollaboration/Shared%20Documents/General/Harmony%20Extracts/Data%20Interface%20Spec%20-%20Requisition%20Creation%20API%20v6.2.docx?d=wab1364a5e68d416fb837d8d3829aa217&csf=1&web=1&e=7HY7O6)

### 2.2.2 Harmony Technical Design Document

Provide a link to the Harmony functional design documentation (if required)
[TBC]()

## 2.3. iBuy Backend Design
### 2.3.1 Data Model and Data flow diagrams

### 2.3.1.1 Attachment Upload and Storage

 **1. User Action:**
- The user uploads an attachment through the iBuy web application using an upload form.

**2. Backend Action:**
- The iBuy application receives the file and its metadata from the user.
- The application calls the Attachment Upload API (`POST /api/attachments`) to handle the upload process.

**3. Storage:**
- The Attachment Upload API stores the file in a dedicated container in Azure Blob Storage.
- The API generates a unique attachment URL, which includes a GUID of 32 characters, and returns it along with the upload status to the iBuy application. 

### 2.3.1.2 Malware Scanning:
**1. Upload Processing:**
-   Microsoft Defender for Storage automatically performs a malware scan on the uploaded attachment.

**2. Scan Result Processing:**
  - Microsoft Defender for Storage sends the scan result to Azure Event Grid.
  - An Azure Function subscribes to Event Grid and processes the scan result:
    - **For Clean Attachments:**
      - The function stores the attachment metadata and scan result in a Cosmos DB database for further reference and tracking.

    - **For Infected Attachments:**
      - The function deletes the attachment from Azure Blob Storage to prevent the spread of malware.
      - It raises an alert to notify relevant stakeholders about the infection.


![image.png](/.attachments/image-ba15e864-3494-4cde-871b-43af1e12ea94.png)

 
_Figure 3_

### 2.3.1.4 Data Transfer to Harmony

**1.Harmony API:** 
   - An Azure Function will directly call the Harmony API with the appropriate payload.
   - The Harmony API creates a record in Harmony, including an obfuscated URI that points to the attachment in Azure Blob Storage.


### 2.3.1.5 Attachment Retrieval:

**1. Request**
- Authorized users or systems initiate the attachment upload by calling the upload API (`POST /api/attachments/upload`).
- The backend responds with a `scanId` and a status polling URL (`GET /api/attachments-status/{scanId}`).

**2. Polling for Scan Status:**
- The frontend regularly checks the scan status every 5 seconds by sending requests to the status polling URL with the `scanId`.
- These polling requests continue until the scan status indicates completion.

**3. Response**


- **Final Response:** If validations pass, the Retrieval Function returns the attachment, along with details indicating whether it is clean or infected.


### 2.3.1.5 Message Response:`

```json
   {
     "status": "success", 
     "scanId": "unique_scan_id", 
     "secure_url": "https://test/65EJDHDB172S.pdf",
     "file_name": "65EJDHDB172S.pdf",
     "attachmentId": "3564-GHDK-DBJDD",   
     "retrievedAt": "2024-06-11T11:00:00Z" 
   }
```
```json
   {
     "status": "failed",
     "scanId": "unique_scan_id",
     "error": "file infected",
     "attachmentId": "3564-GHDK-DBJDD",
     "retrievedAt": "2024-06-11T11:00:00Z"
   }

```

### 2.3.1.6 Public API for Attachment URL Retrieval

- External third-party users or systems can request the attachment URL through a secure Public API (`GET /public-api/attachments/{attachmentId}`).

**2. Request Processing:**
- The Public API allows external systems or users to freely access attachment details using a GET HTTP request with the provided `attachmentId`.

**3. Return Attachment URL:**
- If the attachment is clean and available, the API returns a payload containing the attachment details, including the GUID and any relevant metadata.

**4. Request Limits:**
- To prevent misuse and ensure fair usage of the API, a request limit is enforced. This rate limit controls the number of requests that can be made to the API within a specific time frame, protecting the system from abuse and ensuring availability for all users.




### 2.3.1.6 Message Response:`

```json
{
  "status": "success",
  "attachmentId": "12345",
  "attachmentUrl": "https:/.net/obfuscated-uri"
}
```
```json
{
  "status": "error",
  "message": "Invalid attachment ID."
}

```

### 2.3.2 API / Function Design

### API / Function Design

This section details the new APIs and Azure Function Apps required to implement the feature of securely sharing and managing attachments between iBuy and Harmony.

#### New APIs/Functions Required

### 1. Attachment Upload API

To handle the upload of attachments, store them in Azure Blob Storage, and initiate the malware scan process.

- **Type:** HTTP Trigger Function with Output Binding to Blob Storage
- **Steps:**
  1. **HTTP Trigger**: The API endpoint (`POST /api/attachments`) will be exposed as an HTTP trigger.
  2. **Input Handling**: 
     - Validate the request payload to ensure it includes the file and metadata.
     - Check the file type and size against predefined constraints (allowed types and maximum size).
     - Authenticate the user to ensure they are authorized to upload files (using RBAC validation).
  3. **Blob Storage Binding**: 
     - Store the uploaded file in a dedicated Azure Blob Storage container.
     - Generate a unique URI for the stored file.
  4. **Response**: Return a response with a `scanId`.


### 2. Event Trigger Function

To process the results of the malware scan performed by Microsoft Defender for Storage.

- **Type:** Event Function App triggered by Azure Event Grid
- **Steps:**
  1. **Event Subscription**: Subscribe to events from Azure Event Grid that are related to the completion of the malware scan.

  2. **Outcome Handling**:
     - If the file is clean, update the database to indicate the file is safe and ready to be linked to requisitions.
     - If the file is infected, delete the file from Blob Storage, update the Defender for Storage alert status to "Closed", update the database, and notify the user or the application about the issue.



### 3. Polling Retrieving Attachment Function

To allow the frontend to periodically check the scan status and retrieve the secure URL once the scan is complete.

- **Type:** HTTP Trigger Function
- **Steps:**
  1. **HTTP Trigger**: The API endpoint (`GET /api/scan-status/{scanId}`) will be exposed to handle polling requests.
  2. **Input Handling**:
     - Validate the `scanId` from the request to ensure it is a valid identifier.
  3. **Status Check**:
     - Query the database to retrieve the current scan status associated with the `scanId`.
  4. **Response**:
     - If the scan is complete, return the status and the obfuscated URI of the attachment.
     - If the scan is still in progress, return the current status and a message indicating that the scan is not yet complete.



### 4. Internal API for Attachment Retrieval

To provide secure access to attachments for internal users based on their roles and permissions, retrieving files from Blob Storage using a unique identifier.

- **Type:** HTTP Trigger Function with RBAC Validation
- **Steps:**
  1. **HTTP Trigger**: The internal API endpoint (`GET /internal-api/attachments/{attachmentId}`) will be exposed as an HTTP trigger.
  2. **RBAC Validation**:
     - Authenticate the user and verify their role using role-based access control (RBAC).
     - Ensure the user has the appropriate permissions to access the requested attachment.
  3. **Retrieve Attachment**:
     - Use the provided GUID `(attachmentId)` to locate and fetch the attachment from Azure Blob Storage.
  4. **Response**:
     - Return the attachment in a secure response.
     - If the user does not have the necessary permissions or if the attachment is not found, return an appropriate error message.



### 5. External Public API for Attachment Retrieval

To provide public access to attachments for external users or systems without validation, retrieving files from Blob Storage using a unique identifier.

- **Type:** HTTP Trigger Function without Validation
- **Steps:**
  1. **HTTP Trigger**: The public API endpoint (`GET /public-api/attachments/{guid}`) will be exposed as an HTTP trigger.
  2. **Rate Limiting**:
     - Implement rate limiting to control the frequency of requests and prevent abuse.
  3. **Retrieve Attachment**:
     - Use the provided `(attachmentId)`   to locate and fetch the attachment from Azure Blob Storage.
  4. **Response**:
     - Return the attachment in a secure response.
     - If the attachment is not found or there is an issue with the request, return an appropriate error message.


### 6. Validation during Upload

During the attachment upload process, several validations are necessary to ensure security and compliance with the system's requirements:

1. **File Type Validation**:
   - Only allow specific file types ( PDF, DOCX, XLSX,MSG) to be uploaded.
   - Reject files with disallowed extensions or MIME types.

2. **File Size Validation**:
   - Enforce a file size limit to ensure that individual attachment files are between 10 KB and 35 MB. This prevents excessively small or large files from being uploaded.
   - Return an error message if the uploaded file exceeds the allowed size.

3. **User Authentication and Authorization**:
   - Verify that the user is authenticated and has the necessary permissions to upload files.
   - Use RBAC to check if the user has the correct role to perform the upload operation.

4. **File Integrity Check**:
   - Ensure the file is not corrupted or incomplete by checking the file's metadata and contents.


5. **Secure Storage**:
   - Store the file in a secure and isolated container in Azure Blob Storage to prevent unauthorized access.

6. **Metadata Validation**:
   - Ensure that all required metadata (file name, description, user ID) is provided and valid.
   - Check for any inconsistencies or missing information in the metadata.
