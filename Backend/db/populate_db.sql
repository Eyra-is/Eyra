/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/*
File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
*/

-- basic inserts to start with the "dummy" instructors/devices etc
start transaction;

insert into device (userAgent, imei)
values
    ('Mobile Browser Mozilla etc.', 'NOTAVALIDPHONEID');
insert into instructor (name, email, phone, address)
values
    ('Jane Doe', 'dummy@jk.is', '1-800-DONT-CALL', 'Australia');
insert into speaker (name, deviceImei)
values
    ('John Doe', 'NOTAVALIDPHONEID');
insert into speaker_info (speakerId, s_key, s_value)
values
    (1, 'sex', 'male'),
    (1, 'dob', '1991-1995'),
    (1, 'height', '170');
insert into session (speakerId, instructorId, deviceId, location, start, end, comments)
values 
    (1, 1, 1, 'Norway etc.', '2015/10/1 15:00:00.00', '2015/10/1 15:00:30.05', 'Much wind.');
-- add the special set Random
insert into recording (tokenId, speakerId, sessionId, filename, rec_method)
values
    (1, 1, 1, 'NOTAREALRECORDING', 'eyra');
insert into evaluation_sets (eval_set, recordingId)
values
    ('Random', 1);
insert into recording_agreement (agreement)
values
    ('         <div class="agreement">             <h2>SAMPLE PARTICIPATION AGREEMENT</h2>             <p>This PARTICIPATION AGREEMENT (this "Agreement") dated as of June 4, 2008 is between GMAC LLC, a Delaware limited liability company (the "Seller"), General Motors Corporation, a Delaware corporation ("General Motors"), and Cerberus ResCap Financing LLC, a Delaware limited liability company ("Cerberus Fund", and together with General Motors, each a "Participant" and collectively, the "Participants").</p>             <h2>RECITALS</h2>             <p>WHEREAS, pursuant to that certain Loan Agreement dated as of June 4, 2008 (the "Loan Agreement") by and among Residential Funding Company, LLC, a Delaware limited liability company ("RFC"), GMAC Mortgage, LLC, a Delaware limited liability company ("GMAC Mortgage" and together with RFC, each a "Borrower" and collectively, the "Borrowers"), and Residential Capital, LLC, GMAC Residential Holding Company, LLC, GMAC-RFC Holding Company, LLC, and Homecomings Financial, LLC, as guarantors, the Seller, as the Initial Lender, and GMAC LLC, as the Lender Agent, and other Persons from time to time party thereto, the Seller has agreed to purchase certain existing term loans made to Residential Capital, LLC and provide a revolving credit facility to the Borrowers; and</p>             <p>WHEREAS, to induce the Seller to enter into the Loan Agreement, each of the Participants, who are the indirect owners of the Borrowers and who will obtain benefits from the making of the Loans by the Seller to the Borrowers, has agreed to purchase a participation in the Loans under the Loan Agreement upon the terms and conditions set forth herein.</p>             <p>NOW, THEREFORE, in consideration of the premises and the mutual agreements herein contained, and intending to be legally bound, the Parties hereto agree as follows:</p>             <p>Sample taken from <a href="http://contracts.onecle.com/gm/cerberus-participation-2008-06-04.shtml">http://contracts.onecle.com/gm/cerberus-participation-2008-06-04.shtml</a></p>         </div>         ');

commit;