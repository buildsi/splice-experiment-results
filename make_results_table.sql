-- Uncomment these to create manually from results.csv
-- This is done by pandas connecting to our database:
-- CREATE TABLE results("a" text, "b" text, "original" text, "changed" text, "analysis" text, "time" float, "predictor" text, "prediction" text);
-- These are sqlite (shell) commands, won't work outside of it
-- .mode csv
-- .import results.csv results

-- 'Unknown' results are linker script files
delete from results where original in(select distinct original from results where prediction="Unknown");

-- 'two_predictors' contains all results except those from abi-laboratory
CREATE TABLE two_predictors("a" text, "b" text, "original" text, "changed" text, "analysis" text, "time" float, "predictor" text, "prediction" text);
insert into two_predictors select * from results where predictor<>'abi-laboratory';

-- 'three_predictors' contains all results from predictors except those libraries where abi-lab crashed
CREATE TABLE three_predictors("a" text, "b" text, "original" text, "changed" text, "analysis" text, "time" float, "predictor" text, "prediction" text);
insert into three_predictors select * from results where original not in(select distinct original from results where prediction='Terminated');
