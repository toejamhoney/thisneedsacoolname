import os
import json
import sqlite3
from datetime import datetime

import cfg

class Jobber(object):

    def __init__(self):
        self.db_conn = sqlite3.connect( os.path.join(config.SETTINGS.get('DB_DIR'), 'job_tables.sqlite') )
        self.db_curr = self.db_conn.cursor()
        main_db = "'" + os.path.join(config.SETTINGS.get('DB_DIR'), 'voodo.sqlite') + "'"
        self.db_curr.execute('ATTACH DATABASE ' + main_db + ' AS main_db')
        self.db_conn.commit()
        self.parser = v_parser.JobParser()

    def verify_params(self, params):
        if params:
            return True
        return False

    def add(self, line):
        job_dict = self.parser.parse_args(line)
        new_job = Job(job_dict)
        ret_val = 'Init'
        try:
            job_id = self.insert_job(new_job)
        except (sqlite3.IntegrityError,sqlite3.OperationalError) as err:
            ret_val = 'Failed to add job to database:' + repr(err)
        except Exception as err2:
            print 'ERR:',err2
        else:
            new_job.set('job_id', job_id)
            ret_val = 'Added job to database'
        finally:
            return ret_val

    def insert_job(self, job):
        self.db_curr.execute("SELECT set_id FROM main_db.sample_sets WHERE set_name = '" + job.get('set') + "'")
        self.db_conn.commit()

        data = job.to_JSON()
        row = self.db_curr.fetchone()
        set_id = row[0]
        if not row:
            raise sqlite3.IntegrityError('Invalid sample set name, ' + job.get('set'))
        if not row:
            raise TypeError('Unable to JSON encode job data')

        try:
            self.db_curr.execute('INSERT INTO main_db.jobs (job_name, set_id, dictionary) VALUES (?, ?, ?)', (job.job, set_id, data) )
            self.db_conn.commit()
            job_id = self.db_curr.lastrowid

            self.db_curr.execute('CREATE TABLE job_' + str(job_id) + ' AS SELECT * FROM main_db.samples WHERE set_id = ' + str(set_id))
            self.db_curr.execute('CREATE INDEX idx_' + str(job_id) + ' ON job_' + str(job_id) + '(finished_at, state, sample_id, path)')
            self.db_curr.execute('INSERT INTO queue (job_id, priority, started_at) VALUES (?, ?, ?)', (job_id, job.priority, datetime.now()))
            self.db_conn.commit()
        except (Exception, sqlite3.IntegrityError, sqlite3.OperationalError) as err:
            raise sqlite3.OperationalError(repr(err))
        else:
            return job_id

    def get_a_task(self):
        self.db_curr.execute("SELECT job_id FROM queue WHERE finished_at IS NULL ORDER BY priority LIMIT 1")
        row = self.db_curr.fetchone()
        if not row:
            print 'No jobs found in queue'
            return None
        job_id = row[0]

        self.db_curr.execute("SELECT dictionary FROM main_db.jobs WHERE job_id = " + str(job_id))
        row = self.db_curr.fetchone()
        job_params = json.loads(row[0])

        self.db_curr.execute("SELECT sample_id, path, name FROM job_" + str(job_id) + " WHERE finished_at IS NULL AND state is NULL LIMIT 1")
        row = self.db_curr.fetchone()
        if not row:
            print 'No sample found in job_' + str(job_id)
            self.db_curr.execute("UPDATE queue SET finished_at = ? WHERE job_id = ?", (datetime.now(), job_id) )
            self.db_conn.commit()
            return None
        sample_id = row[0]
        path = row[1]
        name = row[2]

        job_params['job_id'] = job_id
        job_params['sample_id'] = sample_id
        job_params['sample_path'] = path
        job_params['sample_name'] = name
        job_params['host_user'] = config.SETTINGS['HOST_LOG_USERNAME']
        job_params['host_addr'] = config.SETTINGS['HOST_ADDR']
        job_params['host_log_dir'] = config.SETTINGS['LOG_DIR']
        job_params['guest_work_dir'] = config.SETTINGS['GUEST_VOODO_DIR']

        return job_params

    def begin_task(self, id_set):
        self.db_curr.execute("UPDATE job_" + str(id_set[0]) + " SET state=1 WHERE sample_id=" + str(id_set[1]))
        self.db_conn.commit()

    def complete_task(self, id_set):
        self.db_curr.execute("UPDATE job_" + str(id_set[0]) + " SET finished_at=" + str(datetime.now()) + " WHERE sample_id=" + str(id_set[1]))
        self.db_conn.commit()


class Job(object):

    def __init__(self, job_dic):
        self.parameters = job_dic
        self.priority = self.parameters.pop('priority')
        self.job = self.parameters.get('job')
        self.set('log_path', self.parameters.get('job'))
        if self.parameters.get('before'):
            self.set('log_path', os.path.join(self.parameters.get('log_path'), 'before'))
    def complete(self):
        pass
    def set(self, key, value):
        self.parameters[key] = value
    def get(self, key):
        return self.parameters.get(key)
    def to_JSON(self):
        return json.dumps(self.parameters)
    def __str__(self):
        return str(self.parameters)
