-- some rough test inserts just for peace of mind, nothing more
start transaction;

insert into token (inputToken)
values
    ('Snjalli brúni refurinn stökk yfir lata hundinn'),
    ('To be or not to be, that is the question?');
insert into device (hardware, os, software)
values
    ('hp mini TURBO edition', 'debian 5.41', 'chrome browser 37'),
    ('super cluster', 'homebrew OS', 'netscape');
insert into instructor (name, address, phone)
values
    ('muhammad', 'australia', '+012-515-8989'),
    ('john', 'britain', '+0156-823459'),
    ('guðmundur', 'Iceland', '+354-515-0000'),
    ('sirry', 'Norway', '+002999999');
insert into speaker (height, birthdate)
values
    (150, '1991/10/10'),
    (190, '2000/01/01'),
    (220, '1970/12/12');
insert into session (speakerId, instructorId, deviceId, location, start, end, comments)
values 
    (1, 4, 1, 'Norway etc.', '2015/10/1 15:00:00.00', '2015/10/1 15:00:30.05', 'much wind'),
    (1, 2, 2, 'UK', '2015/10/1 16:00:00.00', '2015/10/1 16:01:20.00', 'rain'),
    (2, 2, 2, 'UK', '2015/10/1 10:00:00.00', '2015/10/1 10:00:54.00', 'rain');
insert into recording (tokenId, speakerId, sessionId, duration, rel_path)
values 
    (1, 1, 1, 180500, 'b/a/12345.wav'),
    (2, 1, 1, 180000, 'b/a/2.wav'),
    (2, 3, 2, 350500, 'b/a/3.wav'),
    (1, 3, 1, 184000, 'b/a/4.wav'),
    (1, 1, 3, 30000, 'b/a/e.wav');
    /*(1, 2, 15, 50000, 'b/a/f.wav'); --this should throw an error, since there is no session(id)
                                      --that is 15 (only 3 session entries, starts count at 1) */

rollback;