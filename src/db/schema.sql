-- Xoá bảng cũ theo đúng thứ tự FK, tạo lại — script chạy lại nhiều lần vẫn an toàn.
DROP TABLE IF EXISTS dbo.Attendance;
DROP TABLE IF EXISTS dbo.Events;
DROP TABLE IF EXISTS dbo.Members;

CREATE TABLE dbo.Members (
    member_id   VARCHAR(20)  NOT NULL PRIMARY KEY,
    full_name   NVARCHAR(100) NOT NULL,
    class_name  NVARCHAR(50)  NULL,
    join_date   DATE          NOT NULL,
    role        VARCHAR(20)   NOT NULL,
    position    NVARCHAR(50)  NULL
);

CREATE TABLE dbo.Events (
    event_id    VARCHAR(20)  NOT NULL PRIMARY KEY,
    name        NVARCHAR(200) NOT NULL,
    date        DATE          NOT NULL,
    category    NVARCHAR(50)  NULL,
    event_type  VARCHAR(20)   NOT NULL
);

CREATE TABLE dbo.Attendance (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    member_id     VARCHAR(20)  NOT NULL REFERENCES dbo.Members(member_id),
    event_id      VARCHAR(20)  NOT NULL REFERENCES dbo.Events(event_id),
    checkin_time  DATETIME2    NOT NULL,
    CONSTRAINT UQ_member_event UNIQUE (member_id, event_id)
);