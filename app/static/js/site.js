document.addEventListener("DOMContentLoaded", () => {
    const root = document.documentElement;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const path = window.location.pathname;
    document.querySelectorAll(".navbar .nav-link").forEach((link) => {
        const href = link.getAttribute("href");
        if (href && href !== "/" && path.startsWith(new URL(link.href).pathname)) {
            link.classList.add("active");
        } else if (href === "/" && path === "/") {
            link.classList.add("active");
        }
    });

    document.querySelectorAll("[data-password-toggle], [data_password_toggle]").forEach((button) => {
        const targetKey = button.getAttribute("data-password-toggle") || button.getAttribute("data_password_toggle");
        const input = document.querySelector(
            `[data-password-toggle-target="${targetKey}"], [data_password_toggle_target="${targetKey}"]`
        );

        if (!input) {
            return;
        }

        const label = button.querySelector(".password-toggle-label");

        button.addEventListener("click", () => {
            const shouldShow = input.type === "password";
            input.type = shouldShow ? "text" : "password";
            button.setAttribute("data-password-visible", shouldShow ? "true" : "false");
            button.setAttribute("aria-label", shouldShow ? "Hide password" : "Show password");
            button.setAttribute("aria-pressed", shouldShow ? "true" : "false");
            if (label) {
                label.textContent = shouldShow ? "Hide password" : "Show password";
            }
        });
    });

    document.querySelectorAll("[data-showcase-slider]").forEach((slider) => {
        const rootSection = slider.closest("[data-showcase-root]") || slider;
        const stage = slider.querySelector(".story-showcase-stage");
        const slides = Array.from(slider.querySelectorAll("[data-showcase-slide]"));
        const dots = Array.from(slider.querySelectorAll("[data-showcase-dot]"));
        const prevButton = slider.querySelector("[data-showcase-prev]");
        const nextButton = slider.querySelector("[data-showcase-next]");
        const storyStep = rootSection.querySelector("[data-showcase-story-step]");
        const storyHeadline = rootSection.querySelector("[data-showcase-story-headline]");
        const storyBody = rootSection.querySelector("[data-showcase-story-body]");
        const autoplayDelay = Number.parseInt(slider.dataset.autoplay || "5000", 10);

        if (!stage || !slides.length) {
            return;
        }

        let activeIndex = 0;
        let autoplayId = null;
        let touchStartX = 0;
        let touchStartY = 0;

        const updateStoryCopy = () => {
            const activeSlide = slides[activeIndex];
            if (!activeSlide) {
                return;
            }

            if (storyStep) {
                storyStep.textContent = activeSlide.dataset.stepLabel || "";
            }
            if (storyHeadline) {
                storyHeadline.textContent = activeSlide.dataset.headline || "";
            }
            if (storyBody) {
                storyBody.textContent = activeSlide.dataset.body || "";
            }
        };

        const updatePositions = () => {
            slides.forEach((slide, index) => {
                const distance = (index - activeIndex + slides.length) % slides.length;
                let position = "hidden";

                if (distance === 0) {
                    position = "active";
                } else if (distance === 1) {
                    position = "next";
                } else if (distance === 2) {
                    position = "trail";
                } else if (distance === slides.length - 1) {
                    position = "prev";
                }

                slide.dataset.position = position;
                slide.setAttribute("aria-hidden", distance === 0 ? "false" : "true");
            });

            dots.forEach((dot, index) => {
                const isActive = index === activeIndex;
                dot.setAttribute("aria-pressed", isActive ? "true" : "false");
                if (isActive) {
                    dot.setAttribute("aria-current", "true");
                } else {
                    dot.removeAttribute("aria-current");
                }
            });

            updateStoryCopy();
        };

        const stopAutoplay = () => {
            if (autoplayId) {
                window.clearInterval(autoplayId);
                autoplayId = null;
            }
        };

        const startAutoplay = () => {
            if (prefersReducedMotion || slides.length < 2 || autoplayId) {
                return;
            }

            autoplayId = window.setInterval(() => {
                goTo(activeIndex + 1);
            }, autoplayDelay);
        };

        const restartAutoplay = () => {
            stopAutoplay();
            startAutoplay();
        };

        const goTo = (index, userInitiated = false) => {
            activeIndex = (index + slides.length) % slides.length;
            updatePositions();
            if (userInitiated) {
                restartAutoplay();
            }
        };

        prevButton?.addEventListener("click", () => {
            goTo(activeIndex - 1, true);
        });

        nextButton?.addEventListener("click", () => {
            goTo(activeIndex + 1, true);
        });

        dots.forEach((dot) => {
            dot.addEventListener("click", () => {
                const index = Number.parseInt(dot.dataset.slideIndex || "0", 10);
                goTo(index, true);
            });
        });

        slider.addEventListener("mouseenter", stopAutoplay);
        slider.addEventListener("mouseleave", startAutoplay);
        slider.addEventListener("focusin", stopAutoplay);
        slider.addEventListener("focusout", () => {
            window.setTimeout(() => {
                if (!slider.contains(document.activeElement)) {
                    startAutoplay();
                }
            }, 0);
        });

        stage.addEventListener("keydown", (event) => {
            if (event.key === "ArrowRight") {
                event.preventDefault();
                goTo(activeIndex + 1, true);
            }
            if (event.key === "ArrowLeft") {
                event.preventDefault();
                goTo(activeIndex - 1, true);
            }
        });

        stage.addEventListener(
            "touchstart",
            (event) => {
                const touch = event.changedTouches[0];
                touchStartX = touch.clientX;
                touchStartY = touch.clientY;
                stopAutoplay();
            },
            { passive: true }
        );

        stage.addEventListener(
            "touchend",
            (event) => {
                const touch = event.changedTouches[0];
                const deltaX = touch.clientX - touchStartX;
                const deltaY = touch.clientY - touchStartY;

                if (Math.abs(deltaX) > 40 && Math.abs(deltaY) < 50) {
                    if (deltaX < 0) {
                        goTo(activeIndex + 1, true);
                    } else {
                        goTo(activeIndex - 1, true);
                    }
                    return;
                }

                startAutoplay();
            },
            { passive: true }
        );

        updatePositions();

        if (prefersReducedMotion) {
            slider.dataset.showcaseEntered = "true";
            return;
        }

        window.setTimeout(() => {
            slider.dataset.showcaseEntered = "true";
            startAutoplay();
        }, 240);
    });

    const teamImageModal = document.querySelector("[data-team-image-modal]");
    const teamImageModalImage = teamImageModal?.querySelector("[data-team-modal-image]");
    const teamImageModalTitle = teamImageModal?.querySelector("[data-team-modal-title]");
    const teamImageModalCaption = teamImageModal?.querySelector("[data-team-modal-caption]");
    let lastTeamTrigger = null;

    if (teamImageModal && teamImageModalImage && teamImageModalTitle && teamImageModalCaption) {
        const closeTeamModal = () => {
            teamImageModal.hidden = true;
            document.body.style.removeProperty("overflow");
            if (lastTeamTrigger) {
                lastTeamTrigger.focus();
            }
        };

        document.querySelectorAll("[data-team-modal-trigger]").forEach((trigger) => {
            trigger.addEventListener("click", () => {
                lastTeamTrigger = trigger;
                teamImageModalImage.src = trigger.dataset.teamImageSrc || "";
                teamImageModalImage.alt = trigger.dataset.teamImageAlt || "";
                teamImageModalTitle.textContent = trigger.dataset.teamImageTitle || "EcoBridge Ghana team";
                teamImageModalCaption.textContent = trigger.dataset.teamImageCaption || "";
                teamImageModalCaption.hidden = !teamImageModalCaption.textContent.trim();
                teamImageModal.hidden = false;
                document.body.style.overflow = "hidden";
            });
        });

        teamImageModal.querySelectorAll("[data-team-modal-close]").forEach((button) => {
            button.addEventListener("click", closeTeamModal);
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !teamImageModal.hidden) {
                closeTeamModal();
            }
        });
    }

    const revealTargets = Array.from(
        document.querySelectorAll(
            [
                ".hero-section .eyebrow",
                ".hero-section .hero-kicker",
                ".hero-section .display-title",
                ".hero-section .hero-copy",
                ".hero-section .hero-launch-support",
                ".hero-section .hero-launch-title",
                ".hero-section .btn",
                ".hero-trust-pill",
                ".hero-launch-card",
                ".hero-visual-card",
                ".page-header .eyebrow",
                ".page-header .section-title",
                ".page-header .section-copy",
                ".section-heading-row",
                ".launch-pillar-card",
                ".proof-card",
                ".info-card",
                ".value-anchor-card",
                ".value-support-card",
                ".process-step",
                ".listing-card",
                ".cta-band",
                ".content-panel",
                ".search-panel",
                ".form-panel",
                ".table-panel",
                ".stat-card",
                ".profile-hero",
                ".empty-state",
                ".footer-social-item",
                ".flash-stack .alert",
            ].join(", ")
        )
    );
    const uniqueRevealTargets = [...new Set(revealTargets)];

    uniqueRevealTargets.forEach((element, index) => {
        element.classList.add("reveal-on-scroll");
        element.style.setProperty("--reveal-delay", `${(index % 6) * 125}ms`);
        element.style.setProperty("--reveal-shift-x", `${index % 2 === 0 ? "-18px" : "18px"}`);
        element.style.setProperty("--reveal-tilt", `${index % 2 === 0 ? "-1.75deg" : "1.75deg"}`);
    });

    const markPageLoaded = () => {
        root.classList.add("page-loaded");
    };

    if (prefersReducedMotion) {
        markPageLoaded();
    } else {
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                window.setTimeout(markPageLoaded, 60);
            });
        });
    }

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
        uniqueRevealTargets.forEach((element) => element.classList.add("is-visible"));
        return;
    }

    const revealObserver = new IntersectionObserver(
        (entries, observer) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -10% 0px",
        }
    );

    uniqueRevealTargets.forEach((element) => revealObserver.observe(element));
});
