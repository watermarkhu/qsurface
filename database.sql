CREATE DATABASE cposguf;

CREATE TABLE cases (
  lattice integer NOT NULL,
  p numeric(6,6) NOT NULL,
  target_tot_sims integer NOT NULL,
  target_ubuck_wins integer NOT NULL,
  target_vcomb_wins integer NOT NULL,
  tot_sims integer NOT NULL DEFAULT 0,
  ubuck_sims integer NOT NULL DEFAULT 0,
  vcomb_sims integer NOT NULL DEFAULT 0,
  ubuck_wins integer NOT NULL DEFAULT 0,
  vcomb_wins integer NOT NULL DEFAULT 0,
  PRIMARY KEY (lattice, p)
);

CREATE TABLE computers (
  comp_id varchar(16) PRIMARY KEY,
  cpu_type varchar(64),
  active_lattice integer,
  active_p numeric(6,6),
  CONSTRAINT computer_case_id_fkey FOREIGN KEY (active_lattice, active_p)
    REFERENCES cases (lattice, p) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE simulations (
  sim_id serial PRIMARY KEY,
  lattice integer NOT NULL,
  p numeric(6,6) NOT NULL,
  comp_id varchar(16) NOT NULL,
  created_on timestamp NOT NULL,
  ubuck_solved boolean NOT NULL,
  vcomb_solved boolean NOT NULL,
  error_data text[][][] NOT NULL,
  CONSTRAINT simulations_case_id_fkey FOREIGN KEY (lattice, p)
    REFERENCES cases (lattice, p) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT simulations_comp_id_fkey FOREIGN KEY (comp_id)
    REFERENCES computers (comp_id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE VIEW cases_open AS
    SELECT lattice, p,
    LEAST(tot_sims::numeric/target_tot_sims,
        ubuck_wins::numeric/target_ubuck_wins,
        vcomb_wins::numeric/target_vcomb_wins) progress
    FROM cases
    WHERE tot_sims::numeric/target_tot_sims < 1 AND
        ubuck_wins::numeric/target_ubuck_wins < 1 AND
        vcomb_wins::numeric/target_vcomb_wins < 1;
    ORDER BY lattice, p

CREATE VIEW cases_open_free AS
    SELECT c.lattice, c.p,
    LEAST(tot_sims::numeric/target_tot_sims,
        ubuck_wins::numeric/target_ubuck_wins,
        vcomb_wins::numeric/target_vcomb_wins) progress
    FROM cases c
    LEFT JOIN computers k ON c.lattice = k.active_lattice AND c.p = k.active_p
    WHERE tot_sims::numeric/target_tot_sims < 1 AND
        ubuck_wins::numeric/target_ubuck_wins < 1 AND
        vcomb_wins::numeric/target_vcomb_wins < 1 AND
        k.active_lattice IS NULL OR
        k.active_p IS NULL
    ORDER BY c.lattice, c.p;
