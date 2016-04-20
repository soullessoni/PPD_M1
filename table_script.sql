Drop table VACHE;

Create table VACHE (
	ID char(5) primary key,
	MALADIE char(30),
	PROBABILITE float(8)
);

SELECT * FROM VACHE;

COPY VACHE FROM '/Users/demogetadrien/Desktop/Dataset/test/data1_fiche1.csv';

