
@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """Returns a list of all active/completed jobs"""
    job_list = []
    with job_lock:
        # Convert dict to list
        for jid, job in jobs.items():
            job_list.append(job)
    
    # Sort by created_at desc
    job_list.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    return jsonify({'success': True, 'jobs': job_list})
