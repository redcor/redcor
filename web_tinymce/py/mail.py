from openerp.tools import mail

# Allow iframes to be embedded in HTML fields
# This provides fix for embedding youtube videos
mail.tags_to_kill.remove("iframe")
mail.tags_to_kill.remove("frame")

allow_element_old = mail._Cleaner.allow_element


def allow_element(self, el):
    if el.tag == 'iframe' or el.tag == 'frame':
        return True
    res = allow_element_old(self, el)
    return res


# noinspection PyProtectedMember
mail._Cleaner.allow_element = allow_element
