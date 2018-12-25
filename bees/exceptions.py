class BumbleBeeError(Exception):

    errmsgs = {
        1001: '_GET: resp not ok.',
        1002: '_GET: cannot decode JSON.',
        1003: '_POST: resp not ok.',
        1004: '_POST: cannot decode JSON.'
    }

    def __init__(self, err_code=None):
        if not err_code:
            print('no err_code')
        else:
            msg = self.errmsgs[err_code]
            print(f'Error: {msg}')


class BumbleBeePersonError(BumbleBeeError):
    errmsgs = {
        2001: 'Nothing here yet',
    }


class BumbleBeeAnswerError(BumbleBeeError):
    errmsgs = {
        3001: 'Answer.__init__: must contain "answer_id" or "doc"',
        3002: 'Answer.aloha: this id is not in MongoDB',
    }


class BumbleBeeQuestionError(BumbleBeeError):
    errmsgs = {
        4001: 'Nothing here yet',
    }
