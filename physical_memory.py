
import random


class PhysicalMemory:
    def __init__(self, total_pages, system_pages, replacement_policy):
        if total_pages <= 0 or not 0 <= system_pages <= total_pages:
            raise ValueError("Physical and system page counts are not valid")

        self.total_pages = total_pages
        self.system_pages = system_pages
        self.replacement_policy = replacement_policy.upper()

        if self.replacement_policy not in ("RR", "RND"):
            raise ValueError("Replacement policy must be RR or RND")

        self.page_owners = {}


        self.process_pages = {}

        self.next_free_page = system_pages
        self.released_pages = []
        self.next_victim = system_pages


        self.pages_from_free = 0
        self.page_faults = 0

    def allocate(self, process_id, virtual_page):
        """Return (physical_page, evicted_page).

        evicted_page is None if a free page was used or the page was
        already mapped. If a page was replaced, it is a tuple:
        (physical_page, old_process_id, old_virtual_page).
        """

        pages = self.process_pages.get(process_id, {})
        if virtual_page in pages:
            return pages[virtual_page], None

        evicted_page = None

        if self.released_pages:

            physical_page = self.released_pages.pop()
            self.pages_from_free += 1
        elif self.next_free_page < self.total_pages:

            physical_page = self.next_free_page
            self.next_free_page += 1
            self.pages_from_free += 1
        else:

            if self.system_pages == self.total_pages:
                raise RuntimeError("No physical pages are available to user processes")

            if self.replacement_policy == "RND":
                physical_page = random.randrange(self.system_pages, self.total_pages)
            else:

                physical_page = self.next_victim
                self.next_victim += 1
                if self.next_victim == self.total_pages:
                    self.next_victim = self.system_pages

            old_process, old_virtual_page = self.page_owners[physical_page]
            evicted_page = (physical_page, old_process, old_virtual_page)


            del self.process_pages[old_process][old_virtual_page]
            if not self.process_pages[old_process]:
                del self.process_pages[old_process]
            self.page_faults += 1


        self.page_owners[physical_page] = (process_id, virtual_page)
        self.process_pages.setdefault(process_id, {})[virtual_page] = physical_page
        return physical_page, evicted_page

    def free_process(self, process_id):
        """Release all physical pages used by a finished process.

        Returns their physical page numbers so the caller can invalidate
        related cache entries before those pages are reused.
        """
        pages = self.process_pages.pop(process_id, {})
        freed_pages = []

        for physical_page in pages.values():
            del self.page_owners[physical_page]
            self.released_pages.append(physical_page)
            freed_pages.append(physical_page)

        return freed_pages
