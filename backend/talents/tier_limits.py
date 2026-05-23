"""
Limits por tier — single source of truth para feature gating.

Estos límites se aplican al CREAR (en serializers/views), no son visuales
solamente. Cualquier intento de superar el límite devuelve 403.
"""

# None = ilimitado
TIER_LIMITS = {
    'standard': {
        'max_photos': 5,
        'max_mixes': 2,
        'max_videos': 0,
        'max_packs': 0,
        'max_faqs': 0,
        'max_bio_chars': 200,
        'can_respond_to_reviews': False,
        'can_use_dynamic_pricing': False,
        'can_sync_calendar': False,
    },
    'pro': {
        'max_photos': 10,
        'max_mixes': 4,
        'max_videos': 1,
        'max_packs': 1,
        'max_faqs': 3,
        'max_bio_chars': 500,
        'can_respond_to_reviews': False,
        'can_use_dynamic_pricing': False,
        'can_sync_calendar': False,
    },
    'premium': {
        'max_photos': None,
        'max_mixes': None,
        'max_videos': 4,
        'max_packs': None,
        'max_faqs': None,
        'max_bio_chars': 2000,
        'can_respond_to_reviews': True,
        'can_use_dynamic_pricing': True,
        'can_sync_calendar': True,
    },
}


def get_limits(talent_level):
    """Return the limits dict for a tier, defaulting to standard."""
    return TIER_LIMITS.get(talent_level, TIER_LIMITS['standard'])


def can_add(talent, kind):
    """
    Check if a talent can add another item of `kind`.
    `kind` ∈ {'photo', 'mix', 'video', 'pack', 'faq'}
    Returns (allowed: bool, limit: int|None, current: int).
    """
    limits = get_limits(talent.talent_level)
    key = f'max_{kind}s' if not kind.endswith('s') else f'max_{kind}'
    limit = limits.get(key)
    if limit is None:
        return True, None, 0  # unlimited

    if kind == 'photo':
        current = talent.media.filter(media_type='photo').count()
    elif kind == 'mix':
        current = talent.media.filter(media_type='audio').count()
    elif kind == 'video':
        current = talent.media.filter(media_type='video').count()
    elif kind == 'pack':
        current = talent.packs.count()
    elif kind == 'faq':
        current = talent.faqs.count()
    else:
        return True, None, 0

    return current < limit, limit, current
