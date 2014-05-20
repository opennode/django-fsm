from django.db import models
from django_fsm import FSMField, transition


class STATE:
    PRELIMINARY = 'PRM'
    IRREVOCABLE = 'IRV'

STATE_CHOICES = ((STATE.PRELIMINARY, 'Preliminary', 'PreliminaryReport'),
                 (STATE.IRREVOCABLE, 'Irrevocable', 'IrrevocableReport'))


class SUBMISSION:
    NEW = 'NEW'
    SUBMITTED = 'SBT'
    APPROVED = 'APR'
    REJECTED = 'RJT'

SUBMISSION_CHOICES = ((SUBMISSION.NEW, 'New'),
                      (SUBMISSION.SUBMITTED, 'Submitted'),
                      (SUBMISSION.APPROVED, 'Approved'),
                      (SUBMISSION.REJECTED, 'Rejected'))


class BaseReport(models.Model):
    state = FSMField(state_choices=STATE_CHOICES, default=STATE.PRELIMINARY)
    submission_state = FSMField(choices=SUBMISSION_CHOICES, default=SUBMISSION.NEW)
    text = models.TextField()

    def submit(self):
        pass

    @transition(field=state, source=STATE.PRELIMINARY, target=STATE.IRREVOCABLE)
    @transition(field=submission_state, source=SUBMISSION.APPROVED, target=SUBMISSION.NEW)
    def confirm(self):
        pass

    @transition(field='submission_state', source=SUBMISSION.SUBMITTED, target=SUBMISSION.NEW)
    def approve(self):
        pass

    @transition(field='submission_state', source=SUBMISSION.SUBMITTED, target=SUBMISSION.REJECTED)
    def reject(self):
        pass


class PreliminaryReport(BaseReport):
    """
    Preliminary report could be fixed and resubmitted after reject
    """
    @transition(field='submission_state',
                source=[SUBMISSION.NEW, SUBMISSION.REJECTED],
                target=SUBMISSION.SUBMITTED)
    def submit(self):
        super(PreliminaryReport, self).submit()

    class Meta:
        proxy = True


class IrrevocableReport(BaseReport):
    """
    If preliminay report was approved, final submission could not be resubmitted after rejection
    """
    @transition(field='submission_state',
                source=SUBMISSION.NEW,
                target=SUBMISSION.SUBMITTED)
    def submit(self):
        super(IrrevocableReport, self).submit()

    class Meta:
        proxy = True
