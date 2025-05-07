import js
from wwwpy.remote.component import get_component

from remote.accordion_components import AccordionContainer, AccordionSection


async def test_container_sections():
    # language=html
    js.document.body.innerHTML = """<wwwpy-accordion-container>
    
    <wwwpy-accordion-section>
        <div slot="header">h0</div>
        <div slot="panel">p0</div>
    </wwwpy-accordion-section>
    
    <wwwpy-accordion-section>
        <div slot="header">h1</div>
        <div slot="panel">p1</div>
    </wwwpy-accordion-section>
    
</wwwpy-accordion-container>"""

    accordion_element = js.document.body.firstElementChild
    accordion = get_component(accordion_element, AccordionContainer)
    assert accordion is not None

    assert len(accordion.sections) == 2
    s0, s1 = accordion.sections
    assert isinstance(s0, AccordionSection)
    assert isinstance(s1, AccordionSection)


class TestAccordionSectionStandalone:

    async def test_accordion_should_be_expanded(self):
        # language=html
        js.document.body.innerHTML = """<wwwpy-accordion-section>
        <div slot="header">h0</div>
        <div slot="panel">p0</div>
    </wwwpy-accordion-section>"""

        section = get_component(js.document.body.firstElementChild, AccordionSection)

        assert section.expanded is False

    async def test_expand_should_get_more_space_than_collapse(self):
        # GIVEN

        # language=html
        js.document.body.innerHTML = """<wwwpy-accordion-section>
        <div slot="header">h0</div>
        <div slot="panel">p0</div>"""
        section = get_component(js.document.body.firstElementChild, AccordionSection)

        def height():
            return section.element.getBoundingClientRect().height

        h = height()

        # WHEN
        section.transition = False
        section.expanded = True

        # THEN
        assert height() > h
