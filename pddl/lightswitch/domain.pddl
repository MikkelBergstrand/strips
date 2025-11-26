(define (domain toggle)
  (:predicates
    (on)      ; the switch is on
    (off)     ; the switch is off
  )

  (:action turn-on
    :parameters ()
    :precondition (off)
    :effect (and (on) (not (off)))
  )

  (:action turn-off
    :parameters ()
    :precondition (on)
    :effect (and (off) (not (on)))
  )
)

