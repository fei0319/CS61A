(define (rle s)
    (define (increment s)
        (let ((front (car s)))
            (cons-stream `(,(car front) ,(+ (car (cdr front)) 1)) (cdr-stream s))
        )
    )
    (if (null? s)
        '()
        (if (null? (cdr-stream s))
            (cons-stream `(,(car s) 1) nil)
            (let ((next (rle (cdr-stream s))))
                (if (eq? (car s) (car (cdr-stream s)))
                    (increment next)
                    (cons-stream `(,(car s) 1) next)
                )
            )
        )
    )
)



(define (group-by-nondecreasing s)
    (if(null? s)
        nil
        (if (and (not (null? (cdr-stream s))) (>= (car (cdr-stream s)) (car s)))
            (let ((next (group-by-nondecreasing (cdr-stream s))))
                (cons-stream (cons (car s) (car next)) (cdr-stream next))
            )
            (cons-stream (list (car s)) (group-by-nondecreasing (cdr-stream s)))
        )
    )
)


(define finite-test-stream
    (cons-stream 1
        (cons-stream 2
            (cons-stream 3
                (cons-stream 1
                    (cons-stream 2
                        (cons-stream 2
                            (cons-stream 1 nil))))))))

(define infinite-test-stream
    (cons-stream 1
        (cons-stream 2
            (cons-stream 2
                infinite-test-stream))))

