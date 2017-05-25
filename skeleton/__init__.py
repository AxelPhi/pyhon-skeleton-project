import logging

log = logging.getLogger(__name__)


def sum(a: int, b: int) -> int:
    log.info('Summing up {} ad {} '.format(a, b))
    return a + b
