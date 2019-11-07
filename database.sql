CREATE DATABASE cposguf;

CREATE TABLE cases (
  lattice integer NOT NULL,
  p numeric(6,6) NOT NULL,
  target_tot_sims integer NOT NULL,
  target_tree_wins integer NOT NULL,
  target_list_wins integer NOT NULL,
  tot_sims integer NOT NULL DEFAULT 0,
  tree_sims integer NOT NULL DEFAULT 0,
  list_sims integer NOT NULL DEFAULT 0,
  tree_wins integer NOT NULL DEFAULT 0,
  list_wins integer NOT NULL DEFAULT 0,
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
  n integer,
  comp_id varchar(16) NOT NULL,
  created_on timestamp NOT NULL,
  ftree_tlist boolean NOT NULL,
  seed numeric(24,0) NOT NULL,
  analysis1 boolean NOT NULL DEFAULT False,
  analysis2 boolean NOT NULL DEFAULT False,
  analysis3 boolean NOT NULL DEFAULT False,
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
      tree_wins::numeric/target_tree_wins,
      list_wins::numeric/target_list_wins) progress
  FROM cases
  WHERE tot_sims::numeric/target_tot_sims < 1 AND
      tree_wins::numeric/target_tree_wins < 1 AND
      list_wins::numeric/target_list_wins < 1
  ORDER BY lattice, p;

CREATE VIEW cases_open_free AS
  SELECT lattice, p, progress
  FROM cases_open
  WHERE NOT EXISTS (
    SELECT * FROM computers
    WHERE lattice = active_lattice AND p = active_p
  )
  ORDER BY lattice, p;
