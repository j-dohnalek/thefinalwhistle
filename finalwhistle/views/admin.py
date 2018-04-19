from flask import render_template

from finalwhistle import app

@app.route('/admin', methods=['GET'])
def admin_overview():
    return render_template('admin/index.html')