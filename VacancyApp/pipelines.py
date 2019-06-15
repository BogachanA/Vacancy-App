

USER_FIELDS = ['username', 'email']



def get_list_of_emails():
    return ['bogacbugra@gmail.com','alpgokcek89@gmail.com','thevacancyapp@gmail.com','bogachanarslan@sabanciuniv.edu','gokcekal@mef.edu.tr']


def create_user(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    allowed_emails = get_list_of_emails()
    print("inside overrriden pipeline")

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in strategy.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    if fields['email'] in allowed_emails:
        return {
            'is_new': True,
            'user': strategy.create_user(**fields)
        }

    return