-- create a table
/*CREATE TABLE test(
  id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name TEXT NOT NULL,
  archived BOOLEAN NOT NULL DEFAULT FALSE
);

-- add test data
INSERT INTO test (name, archived)
  VALUES ('test row 1', true),
  ('test row 2', false);
*/

-- lines to drop all tables
/*
drop schema public cascade;
create schema public;
*/


-- create tables
CREATE TABLE Personne(
  idPersonne INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  nom TEXT NOT NULL,
  prenom TEXT NOT NULL,
  mail TEXT NOT NULL UNIQUE CHECK (mail ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
  password TEXT NOT NULL CHECK (length(password) >= 8),
  role TEXT NOT NULL,
  last_login TEXT DEFAULT NULL,
  is_superuser BOOLEAN DEFAULT FALSE,
  is_staff BOOLEAN DEFAULT True,
  is_active BOOLEAN DEFAULT True
);

CREATE TABLE Delivrable(
  idDelivrable INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  typeFichier TEXT check(typeFichier IN ('pdf', 'docx', 'pptx', 'xlsx', 'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'tgz', 'tbz2', 'txz', 'pdf', 'docx', 'pptx', 'xlsx', 'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'tgz', 'tbz2', 'txz'))
);


CREATE TABLE Periode(
  idPeriode INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  annee int NOT NULL
  );
CREATE TABLE Etape(
  idEtape INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  dateDebut DATE NOT NULL,
  dateFin DATE NOT NULL,
  description TEXT NOT NULL,
  idPeriode INT NOT NULL,
  idDelivrable INT,
  FOREIGN KEY (idPeriode) REFERENCES Periode(idPeriode),
  FOREIGN KEY (idDelivrable) REFERENCES Delivrable(idDelivrable)
);
CREATE TABLE Professeur(
  idProf INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  specialite TEXT,
  idPersonne INT NOT NULL,
  idPeriode INT NOT NULL,
  FOREIGN KEY (idPersonne) REFERENCES Personne(idPersonne),
  FOREIGN KEY (idPeriode) REFERENCES Periode(idPeriode)
);

CREATE TABLE UE(
  idue TEXT PRIMARY KEY, -- matricule de l'UE
  nom TEXT NOT NULL,
  idProf INT NOT NULL,
  FOREIGN KEY (idProf) REFERENCES Professeur(idProf)
);
CREATE TABLE Cours(
  idCours INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  idue TEXT,
  nom TEXT NOT NULL,
  idEtudiant INT,
  FOREIGN KEY (idUE) REFERENCES UE(idUE)
);

CREATE TABLE Sujet(
  idSujet INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  titre TEXT NOT NULL,
  descriptif TEXT NOT NULL DEFAULT 'NULL',
  destination TEXT NOT NULL DEFAULT 'NULL',
  estReserve BOOLEAN NOT NULL DEFAULT FALSE,
  fichier TEXT, --  localisation du fichier de la proposition de sujet
  nbPersonnes INT NOT NULL DEFAULT 1,
  idPeriode INT NOT NULL DEFAULT 1,
  idProfesseur INT,
  idSuperviseur INT,
  idUE TEXT NOT NULL,
  FOREIGN KEY (idPeriode) REFERENCES Periode(idPeriode),
  FOREIGN KEY (idProfesseur) REFERENCES Professeur(idProf)


);
CREATE TABLE Etudiant(
  idEtudiant INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  bloc INT NOT NULL check(bloc >= 1 and bloc <= 5),
  idPersonne INT NOT NULL,
  FOREIGN KEY (idPersonne) REFERENCES Personne(idPersonne)
);

CREATE TABLE FichierDelivrable(
  idFichier INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  fichier TEXT NOT NULL,
  idEtudiant INT,
  idDelivrable INT,
  estRendu BOOLEAN NOT NULL DEFAULT FALSE,
  note INT check ( note >= 0 and note <= 20),
  estConfidentiel BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (idEtudiant) REFERENCES Etudiant(idEtudiant),
  FOREIGN KEY (idDelivrable) REFERENCES Delivrable(idDelivrable)
);

CREATE TABLE Superviseur(
  idSuperviseur INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  specialite TEXT NOT NULL,
  idPersonne INT NOT NULL,
  FOREIGN KEY (idPersonne) REFERENCES Personne(idPersonne)
);

CREATE TABLE Supervision(
  idSupervision INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  description TEXT NOT NULL,
  idSuperviseur INT NOT NULL,
  idUe TEXT NOT NULL,
  FOREIGN KEY (idSuperviseur) REFERENCES Superviseur(idSuperviseur),
  FOREIGN KEY (idUe) REFERENCES UE(idUe)
);
CREATE TABLE SelectionSujet(
  idSelection INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  idSujet INT NOT NULL,
  idEtudiant INT NOT NULL,
  FOREIGN KEY (idSujet) REFERENCES Sujet(idSujet),
  FOREIGN KEY (idEtudiant) REFERENCES Etudiant(idEtudiant)
);

CREATE TABLE EtapeUe(
  idEtapeUe INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  idEtape INT NOT NULL,
  idUe TEXT NOT NULL,
  etapeCourante BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (idEtape) REFERENCES Etape(idEtape),
  FOREIGN KEY (idUe) REFERENCES UE(idUe)
);


-- create a function
-- first trigger
CREATE OR REPLACE FUNCTION check_idprof_idsuperviseur() RETURNS TRIGGER AS $$
     DECLARE idProf INT;
     DECLARE idSupervis INT;
BEGIN
   select idProfesseur into idProf from sujet where Sujet.idProfesseur = NEW.idProfesseur;
   select Sujet.idSuperviseur into idSupervis from sujet where Sujet.idSuperviseur = NEW.idSuperviseur;

    IF NEW.idprofesseur IS NOT NULL AND NEW.idsuperviseur IS NOT NULL THEN
        RAISE EXCEPTION 'Un sujet ne peut pas avoir à la fois un idProf et un idsuperviseur. Un des deux doit être NULL.';
    END IF;

   IF idProf IS NOT NULL and idSupervis IS NULL THEN
       RETURN NEW;
    END IF;
   IF NEW.idprofesseur is NULL and NEW.idsuperviseur is not NULL THEN
       RETURN NEW;
    END IF;
    IF NEW.idprofesseur IS NOT NULL and NEW.idsuperviseur IS NULL THEN
        RETURN NEW;
    END IF;
END
$$ LANGUAGE plpgsql;
-- second trigger
CREATE OR REPLACE FUNCTION check_not_below_for_assignation_for_a_subject() RETURNS TRIGGER AS $$
      DECLARE nbPersonnesForSujet INT;
      DECLARE nbPersonnesEffectif INT;
      DECLARE est_reserve BOOLEAN;
      DECLARE nbPersonneAffecte INT;
BEGIN
  select nbPersonnes into nbPersonnesForSujet from sujet where Sujet.idSujet = NEW.idSujet;
  select count(*) into nbPersonnesEffectif from selectionsujet where SelectionSujet.idSujet = NEW.idSujet;
  select est_reserve into est_reserve from sujet where Sujet.idSujet = NEW.idSujet;

  IF est_reserve = TRUE THEN
    RAISE EXCEPTION 'Le sujet est déjà pris';
  ELSE
    nbPersonneAffecte := nbPersonnesForSujet - nbPersonnesEffectif;
    IF nbPersonneAffecte >= 1 THEN
      RETURN NEW;
    ELSE
      RAISE EXCEPTION 'Le nombre de personnes pour ce sujet est atteint';
    END IF;
  END IF;

END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_reserve_to_true() RETURNS TRIGGER AS $$
    DECLARE nbPersonnesForSujet INT;
    DECLARE nbPersonnesEffectif INT;
    DECLARE nbPersonneAffecte INT;
BEGIN
    select nbPersonnes into nbPersonnesForSujet from sujet where Sujet.idSujet = NEW.idSujet;
    select count(*) into nbPersonnesEffectif from selectionsujet where SelectionSujet.idSujet = NEW.idSujet;

    nbPersonneAffecte := nbPersonnesForSujet - nbPersonnesEffectif;

    IF nbPersonneAffecte = 0 THEN
        -- RAISE NOTICE '%', nbPersonneAffecte; Cette ligne permet d'afficher des informations à la console
        UPDATE Sujet SET estreserve = TRUE WHERE idSujet = NEW.idSujet;        
        RETURN NEW;
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

--create trigger
CREATE TRIGGER unique_teacher_or_supervisor_for_a_subject
  BEFORE INSERT OR UPDATE
  ON sujet
  FOR EACH ROW when (NEW.idProfesseur IS NOT NULL OR NEW.idsuperviseur IS NOT NULL)
    EXECUTE FUNCTION check_idprof_idsuperviseur();

CREATE TRIGGER not_below_for_assignation_for_a_subject
  BEFORE INSERT OR UPDATE
  ON selectionsujet
  FOR EACH ROW when (NEW.idSujet IS NOT NULL OR NEW.idEtudiant IS NOT NULL)
    EXECUTE FUNCTION check_not_below_for_assignation_for_a_subject();

CREATE TRIGGER est_reserve
  BEFORE INSERT OR UPDATE
  ON selectionsujet
  FOR EACH ROW when ( NEW.idSujet IS NOT NULL OR NEW.idEtudiant IS NOT NULL)
    EXECUTE FUNCTION set_reserve_to_true();

-- add insertion data
INSERT INTO Personne (nom, prenom, mail,password, role)
  VALUES ('Doe', 'John', 'john.doe@gmail.com', 'pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=',
          '{"role" : ["etudiant"], "view": "etudiant"}'),
        ('Doe', 'Jane', 'jane.doe@gmail.com','pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=','{"role" : ["etudiant"], "view": "etudiant"}'),
        ('Doe', 'Rick','ricke.doe@gmail.com','pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=','{"role" : ["etudiant"], "view": "etudiant"}'),
        ('Doe', 'Rudolf','rudolf.doe@gmail.com','pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=','{"role" : ["etudiant"], "view": "etudiant"}'),
        ('Doe', 'Jack', 'jack.doe@gmail.com','pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=','{"role" : ["professeur","superviseur"], "view": "professeur"}'),
        ('Doe', 'Jill', 'jill.doe@gmail.com','pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=',' {"role" : ["professeur"], "view": "professeur"}'),
        ('Doe', 'James', 'james.doe@gmail.com','pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=', '{"role" : ["admin"], "view": "admin"}'),
        ('Doe', 'Jenny', 'jenny.doe@gmail.com','pbkdf2_sha256$720000$tjC57NAqNFX9F7XCKvDqet$ymUne1VQexTF3EB/sqF+eqJSC8ZC4F9wgrSUblI9iPw=','{"role": ["superviseur"], "view": "superviseur"}');
INSERT INTO Periode (annee)
  VALUES (EXTRACT(YEAR FROM TIMESTAMP '2023-01-01')),
        (EXTRACT(YEAR FROM TIMESTAMP '2024-01-01'));

INSERT INTO Delivrable (typeFichier)
  VALUES ('pdf'),
        ('docx');
INSERT INTO Etape (dateDebut, dateFin, description, idPeriode, idDelivrable)
  VALUES ('2023-09-01','2024-01-01', 'rendre le devoir de IDS', 1, 1),
        ('2023-09-01','2024-02-01', 'rendre le mémoire', 2, 2);

INSERT INTO Professeur (specialite, idPersonne, idPeriode)
  VALUES ('IA', 5, 1),
        ('ML', 6, 2);

INSERT INTO UE (idue,nom, idProf)
  VALUES ('INFOB331','Introduction à la démarche scientifique', 1),
        ('INFOMA451','Mémoire', 2);
INSERT INTO Cours (idUE, nom)
  VALUES ('INFOB331', 'Introduction à la démarche scientifique'),
        ('INFOMA451', 'Mémoire');
INSERT INTO Sujet (titre, descriptif, fichier, idPeriode, idProfesseur,estReserve,idSuperviseur,idUE,nbPersonnes)
    VALUES ('La reproduction des insectes', 'Les insectes sont des animaux ovipares', NULL, 1, NULL,FALSE,1,'INFOB331',1),
          ('L IA', 'L intelligence artificelle est un système informatique capable d apprendre par lui-même', NULL, 2,1,FALSE,NULL,'INFOMA451',2);
INSERT INTO Etudiant (bloc, idPersonne)
  VALUES (1, 1 ),
        (2, 2);
INSERT INTO Etudiant(bloc, idPersonne)
      VALUES  (3, 3),
        (4, 4);


INSERT INTO Superviseur (specialite, idPersonne)
  VALUES
  ('IA', 8),
  ('ML', 5);

INSERT INTO Supervision (description, idSuperviseur, idUe)
  VALUES
  ('Supervision de l UE INFOB331', 1, 'INFOB331'),
  ('Supervision de l UE INFOMA451', 2, 'INFOMA451');

INSERT INTO SelectionSujet (idSujet, idEtudiant)
  VALUES
  (2,2);
  
INSERT INTO EtapeUe (idEtape, idUe, etapeCourante)
  VALUES (1, 'INFOB331', TRUE),
        (2, 'INFOMA451', TRUE);


alter table Cours ADD FOREIGN KEY (idetudiant) REFERENCES Etudiant(idetudiant);

Update Cours Set idetudiant = 1 where idCours = 1;
UPDATE COURS SET idEtudiant = 2 where idCours = 2;

alter table Sujet ADD FOREIGN KEY (idSuperviseur) REFERENCES Superviseur(idSuperviseur);
alter table Sujet ADD FOREIGN KEY (idue) REFERENCES UE(idue);





