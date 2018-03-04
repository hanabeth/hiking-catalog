
from flask import Flask
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, TreeGenus, TreeEntry

app = Flask(__name__)

# Create session and connect to the database.
engine = create_engine('sqlite:///treegenuscatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/genus/<int:genus_id>/')

@app.route('/genus/<int:genus_id>/list/JSON')
def treeGenusJSON(genus_id):
    genus = session.query(TreeGenus).filter_by(id=genus_id).one()
    tree = session.query(TreeEntry).filter_by(genus_id=genus_id).all()
    return jsonify(TreeEntries=[i.serialize for i in entries])

@app.route('/genus/<int:genus_id>/list/<int:tree_id>/JSON')
def treeEntryJSON(genus_id, tree_id):
    Tree_Entry = session.query(TreeEntry).filter_by(id=tree_id).one()
    return jsonify(Tree_Entry=Tree_Entry.serialize)

@app.route('/genus/JSON')
def generaJSON():
    genera = session.query(TreeGenus).all()
    return jsonify(genera=[g.serialize for g in genera])





# Show all genus
@app.route('/')
@app.route('/genus/')
def showGenera():
    genera = session.query(TreeGenus).all()
    # return "This page will show all tree genera"
    return render_template('genera.html', genera=genera)


# Create a new genus
@app.route('/genus/new/', methods=['GET', 'POST'])
def newGenus():
    if request.method == 'POST':
        newGenus = TreeGenus(name=request.form['name'])
        session.add(newGenus)
        session.commit()
        return redirect(url_for('showGenera'))
    else:
        return render_template('newGenus.html')
    # return "This page will be for making a new genus"


# Edit a restaurant
@app.route('/genus/<int:genus_id>/edit/', methods=['GET', 'POST'])
def editGenus(genus_id):
    editedGenus = session.query(
        TreeGenus).filter_by(id=genus_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedGenus.name = request.form['name']
            return redirect(url_for('showGenus'))
    else:
        return render_template(
            'editGenus.html', restaurant=editedGenus)

    # return 'This page will be for editing genus %s' % genus_id


# Delete a genus
@app.route('/genus/<int:genus_id>/delete/', methods=['GET', 'POST'])
def deleteGenus(genus_id):
    genusToDelete = session.query(
        TreeGenus).filter_by(id=genus_id).one()
    if request.method == 'POST':
        session.delete(genusToDelete)
        session.commit()
        return redirect(
            url_for('showGenera', genus_id=genus_id))
    else:
        return render_template(
            'deleteGenus.js', restaurant=genusToDelete)
    # return 'This page will be for deleting genus %s' % genus_id


# Show a genus list
@app.route('/genus/<int:genus_id>/')
@app.route('/genus/<int:genus_id>/list/')
def showMenu(genus_id):
    genus = session.query(TreeGenus).filter_by(id=genus_id).one()
    entries = session.query(TreeEntry).filter_by(
        genus_id=genus_id).all()
    return render_template('list.html', entries=entries, genus=genus)
    # return 'This page is the menu for genus %s' % genus_id


# Create a new tree entry
@app.route(
    '/genus/<int:genus_id>/list/new/', methods=['GET', 'POST'])
def newMenuItem(genus_id):
    if request.method == 'POST':
        newEntry = TreeEntry(name=request.form['name'], description=request.form[
                           'description'], scientific_name=request.form['scientific_name'], location=request.form['location'], genus_id=genus_id),
        					environment=request.form['environment'],
        session.add(newEntry)
        session.commit()

        return redirect(url_for('showList', genus_id=genus_id))
    else:
        return render_template('newtreeentry.html', genus_id=genus_id)

    return render_template('newTreeEntry.html', genus=genus)
    # return 'This page is for making a new tree entry for genus %s'
    # %genus_id


# Edit a tree entry
@app.route('/genus/<int:genus_id>/list/<int:tree_id>/edit',
           methods=['GET', 'POST'])
def editTreeEntry(genus_id, tree_id):
    editedTree = session.query(TreeEntry).filter_by(id=tree_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedEntry.name = request.form['name']
        if request.form['description']:
            editedEntry.description = request.form['description']
        if request.form['location']:
            editedEntry.price = request.form['location']
        if request.form['environment']:
            editedEntry.course = request.form['environment']
        session.add(editedEntry)
        session.commit()
        return redirect(url_for('showList', genus_id=genus_id))
    else:

        return render_template(
            'edittreeentry.html', genus_id=genus_id, list_id=list_id, entry=editedEntry)
    # return 'This page is for editing tree entry %s' % list_id


# Delete a tree entry
@app.route('/genus/<int:genus_id>/list/<int:list_id>/delete',
           methods=['GET', 'POST'])
def deleteTreeEntry(genus_id, list_id):
    entryToDelete = session.query(TreeEntry).filter_by(id=list_id).one()
    if request.method == 'POST':
        session.delete(entryToDelete)
        session.commit()
        return redirect(url_for('showList', genus_id=genus_id))
    else:
        return render_template('deleteTreeEntry.html', entry=entryToDelete)
    # return "This page is for deleting tree entry %s" % list_id


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

