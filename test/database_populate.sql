INSERT INTO tokens (username, token, admin, valid_until) VALUES ('john.doe', 'qwertyuiop123456789', TRUE, '2099-12-31T23:59:59Z');
INSERT INTO tokens (username, token, admin, valid_until) VALUES ('john.invalid', 'qwertyuiop123456789', TRUE, '2020-12-31T23:59:59Z');
INSERT INTO tokens (username, token, admin, valid_until) VALUES ('jack.valid', '0123456789asdfghjkl', FALSE, '2099-12-31T23:59:59Z');
INSERT INTO tokens (username, token, admin, valid_until) VALUES ('jack.invalid', '12345zxcvbnm67890', FALSE, '2020-12-31T23:59:59Z');
