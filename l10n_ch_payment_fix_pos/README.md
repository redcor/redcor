https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-13.0
https://github.com/odoo/odoo/blob/13.0/doc/python3.rst


if you use reports, report module has been split between base and web:

    Change all references of ir.actions.report.xml by ir.actions.report, as the model has been changed.
    Replace t-call occurrences of base report templates:
        report.external_layout > web.external_layout.
        report.external_layout_header: No direct equivalent. You need to insert the changes inside div class="header o_clean_header"> element of the web.external_layout_? view, being ? one of the available "themes" (background, boxed, clean and standard in core)
        report.external_layout_footer: the same as above, but looking inside <div class="footer o_background_footer"> element.
        report.html_container > web.html_container.
        report.layout > web.report_layout.
        report.minimal_layout > web.minimal_layout.
