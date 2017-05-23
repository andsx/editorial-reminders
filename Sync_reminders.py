#! python3
import reminders
import datetime
import workflow


todos = []
lastidx = 0
index = 0
action_in = workflow.get_input()
lines = action_in.splitlines()


def get_task(line):
    task = line.partition('- ')[2]
    task, split, tags = task.partition(' @')
    done = False
    donedate = None
    duedate = None
    if tags != '':
        for tag in str(tags).split(' @'):
            if tag[:4] == 'done':
                done = True
                donedate = datetime.datetime.strptime(tag[5:15], '%Y-%m-%d')
            if tag[:3] == 'due':
                duedate = datetime.datetime.strptime(tag[4:14], '%Y-%m-%d')
    return task, done, donedate, duedate


def get_calendar(line):
    project = line[:-1]
    for cal in reminders.get_all_calendars():
        if cal.title == project:
            todo = reminders.get_reminders(cal)
            return cal, todo
    return None, []


def sync_tptask(line, curcal):
    task, done, donedate, duedate = get_task(line)
    for todo in todos:
        if todo.title == task:
            if done and not todo.completed:
                todo.completed = True
                todo.completion_date = donedate
                todo.save()
            if not done and todo.completed:
                lines[index] += ' @done('
                lines[index] += str(todo.completion_date.strftime('%Y-%m-%d'))
                lines[index] += ')'
            todos[:] = [todo for todo in todos if todo.title != task]
            return
    newtodo = reminders.Reminder(curcal)
    newtodo.title = task
    newtodo.completed = done
    newtodo.completion_date = donedate
    newtodo.save()


def sync_caltasks(lines):
    if len(todos) > 0:
        for td in todos:
            task = '- ' + td.title
            if td.completed:
                task += ' @done('
                task += str(td.completion_date.strftime('%Y-%m-%d')) + ')'
            lines.insert(lastidx + 1, task)


for index, line in enumerate(lines[:]):
    line = line.strip()
    if line.endswith(':'):
        sync_caltasks(lines)
        cal, todos = get_calendar(line)
        lastidx = index
    elif line.startswith('- ') and cal is not None:
        sync_tptask(line, cal)
        lastidx = index
sync_caltasks(lines)
action_out = ('\n'.join(lines))

workflow.set_output(action_out)
